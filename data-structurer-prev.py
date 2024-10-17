import json
from time import sleep

from openai import OpenAI
import pandas as pd
from dotenv import dotenv_values 

from constants import FUNCTIONS, PROMPT, get_scraped_iteration, get_extracted_iteration
from utils import logger

secrets = dotenv_values(".env")
client = OpenAI(api_key=secrets["OPEN_AI_API_KEY"])

processed_ids = pd.read_csv('./extracted/processed/done_ids.csv')
system_message = {"role": "system", "content": PROMPT}

data_df = None
seed_df = None
data_filtered_df = None
 
"""
Did this patter so that things dont run on import. And only get run when run_extractor() is called.
subtract by scraped_iteration by 1 since we want to use the scraped csv from the previous iteration and  we increment scraped iteration soon as we finish scraping
"""
def set_up_df():
    OPENAI_EXTRACTED_CSV = f'./extracted/extracted-{get_extracted_iteration()}.csv'
    SCRAPED_CSV = f'./scraped/scraped-{get_scraped_iteration() - 1}.csv'
    global seed_df
    global data_df
    try:
        seed_df = pd.read_csv(OPENAI_EXTRACTED_CSV)
    except:
        seed_df = pd.DataFrame(columns=['post_id', 'rent', 'size', 'location', 'specific_location', 'type_of_posting', 'phone_number'])
        print('no file found for already extracted')
    data_df = pd.read_csv(SCRAPED_CSV)
    data_df.fillna('', inplace=True)

def print_separator():
    print("====================================\n")

def remove_duplicates():
    # from data_df remove rows which have same post_text(keep only one)
    data_df.drop_duplicates(subset=['post_text'], inplace=True)

# all processed ids are in processed ids. We load as int64 since i copy pasted from scrape
def remove_processed_ids(df):
    df['post_id'] = df['post_id'].astype('int64')
    df = df[~df.post_id.isin(processed_ids.post_id)]
    return df

def remove_empty_post_text(df):
    df = df[df.post_text != '']
    return df

def structure(post_message):
    return {"role": "user", "content": post_message}

"""
Try three times since openai api is flaky: sometimes times out
"""
def extract_data(post_message):
    retries = 3
    if not post_message: return None 
    for trials in range(retries):
        try:
            chat_completion = client.chat.completions.create(model="gpt-3.5-turbo", temperature=0, messages=[system_message, structure(post_message)])
            choice = chat_completion.choices[0].message
            return choice
        except Exception as e:
            logger.error(f'OpenAI extract failed: {e}')
            print(f'Open AI call failed on attempt {trials + 1}')
            delay = 2 ** trials
            print(f'retrying in {delay} seconds')
            sleep(delay)
    return None

def get_formatted_data(post_message):
    if not post_message: return None 
    chat_completion = client.chat.completions.create(model="gpt-3.5-turbo", temperature=0.3, messages=[structure(post_message)], functions=FUNCTIONS, function_call={"name": "return_structured_data"})
    choice = chat_completion.choices[0].message
    print('parsing text using openai')
    if choice.get('function_call'):
        print(f"calling function {choice['function_call']['name']}")
        function_args = choice['function_call']['arguments']
        try:
            jsonny = json.loads(function_args)
            return jsonny
        except:
            print('error parsing json')
    print('no function call')
    return None 



def get_formatted_data_without_functions(post_message):
    print('calling openai api')
    choice = extract_data(post_message)
    if (choice == None): return None
    print(f'Text from openai: {choice.content}')
    try:
        jsonny = json.loads(choice.content)
        return jsonny
    except:
        logger.warning(f'Error parsing json: {post_message}')
        print('error parsing json')
    return(None)

def add_data(rent, size, location,specific_location, type_of_posting, phone_number, post_id):
    print('adding data to seed')
    seed_df.loc[len(seed_df.index)] = [post_id, rent, size, location, specific_location, type_of_posting, phone_number]
    seed_df.to_csv(f'./extracted/extracted-{get_extracted_iteration()}.csv', index=False)
    global processed_ids
    # merge the processed ids with the seed_df and save it as csv 
    processed_ids = pd.concat([processed_ids, seed_df[['post_id']]], ignore_index=True)
    processed_ids = processed_ids.drop_duplicates(subset=['post_id'])
    processed_ids.to_csv('./extracted/processed/done_ids.csv', index=False)

def apply_shit(data):
    id = data['post_id']
    message = data['post_text']
    print(f'in process, post id {id}')
    json_data = get_formatted_data_without_functions(message)
    if json_data:
        add_data(post_id=id, rent=json_data.get('rent'), location=json_data.get('location'), size=json_data.get('size'), specific_location=json_data.get('specific_location'), type_of_posting=json_data.get('type_of_posting'), phone_number=json_data.get('phone_number'))
    print_separator()

def add_to_seed(rent, size, location, image_uris):
    seed_df.loc[len(seed_df.index)] = [rent, size, location, image_uris]

def dowork():
    data_df.apply(apply_shit, axis=1)

def run_extractor():
    set_up_df()
    remove_duplicates()
    global data_df
    data_df = remove_empty_post_text(data_df)
    data_df = remove_processed_ids(data_df)
    dowork()

if __name__ == "__main__": 
    run_extractor()