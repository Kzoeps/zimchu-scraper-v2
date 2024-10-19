import requests
import pandas as pd
from requests.adapters import HTTPAdapter, Retry
from dotenv import dotenv_values 
import requests
import json
from time import sleep

from utils import breaker
from supabase_zimchu import create_client, Client
from uuid import uuid4
from constants import get_migration_iteration
from utils import logger

url: str  = dotenv_values(".env")["SUPABASE_URL"]
key: str = dotenv_values(".env")["SUPABASE_ADMIN"]
storage_url: str = dotenv_values(".env")["SUPABASE_STORAGE_URL"]
done = pd.read_csv('./images/processed/done_ids.csv')
df = pd.DataFrame(columns=['og_uri', 'ref_name' , 'supabase_uri'])

supabase: Client = create_client(url, key)
res = supabase.storage.get_bucket('listings')

def get_bucket_path(post_id, image_id):
    return f'{post_id}/{image_id}'

def create_uri(post_id, image_id):
    return f'{storage_url}/{get_bucket_path(post_id, image_id)}'

def add_image_uri(image_uri, post_id, image_id):
    df.loc[len(df.index)] = [image_uri, get_bucket_path(post_id, image_id), create_uri(post_id, image_id)]

def create_optimistic_image_uris(post_id, image_uris):
    optimistic_image_uris = []
    for uri in image_uris:
        image_id = uuid4()
        add_image_uri(uri, post_id, image_id)
        optimistic_image_uris.append(create_uri(post_id, image_id))
    return json.dumps(optimistic_image_uris)

def save_images_df():
    df.to_csv(f'./images/image-{get_migration_iteration()}.csv', index=False)

def add_to_done(path):
    done.loc[len(done.index)] = [path]
    done.to_csv('./images/processed/done_ids.csv', index=False)

def get_image_from_fb(image_uri):
    if image_uri == 'nan':
        return None
    print(f'getting image from: {image_uri}\n')
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    try:
        response = session.get(image_uri)
        response.raise_for_status()
        return bytes(response.content)
    except Exception as e:
        logger.error(f'Error getting image: {e}, image_uri: {image_uri}')
        error = f"Error getting image: {e}"
        print(error)
        return None

def upload_image(image_uri,path):
    breaker()
    # delete after testing
    # print(f'getting image from: {image_uri}\n')
    # res = requests.get(image_uri)
    # if (res.content and res.status_code == 200):
    #     image =  bytes(res.content)
    #     print(f'uploading image to {path}')
    #     res = supabase.storage.from_('listings').upload(path, image, {'contentType': 'image/png'})
    #     if res.status_code == 200:
    #         add_to_done(path)
    retries = 3
    image = get_image_from_fb(image_uri)
    if (image!=None):
        for attempt in range(retries):
            try:
                print(f'uploading image to {path}; attempt {attempt + 1}')
                response = supabase.storage.from_('listings').upload(path, image, {'contentType': 'image/png'})
                if response.status_code == 200:
                    add_to_done(path)
                    return
                else:
                    raise Exception(f"Supabase upload failed with status code: {response.status_code}; Error: {response.content}")
            except Exception as e:
                logger.error(f'Error uploading image: {e}, image_path: {path}')
                print(f'Error uploading image: {e}')
                delay = 2 ** attempt
                print(f'retrying in {delay} seconds')
                sleep(delay)

def storage(data):
    image_uri = (data['og_uri'])
    path = data['ref_name']
    upload_image(image_uri, path)

def clean_up(df):
    df.drop_duplicates(subset=['og_uri'], inplace=True)
    df.drop_duplicates(subset=['ref_name'], inplace=True)
    df = df[~df.ref_name.isin(done.ref_name)]
    return df

# remove if the row has been deleted from supabase
def clean_up_from_supabase(df):
    listing_df =pd.read_csv(f'./for-supabase/listing-{get_migration_iteration()}.csv')
    unique_ids = list(map(str,listing_df.id.unique()))
    df = df[df.ref_name.str.contains('|'.join(unique_ids))]
    return df

def store_images():
    images_df = pd.read_csv(f'./images/image-{get_migration_iteration()}.csv')
    images_df = clean_up(images_df)
    images_df = clean_up_from_supabase(images_df)
    images_df.apply(storage, axis=1)

if __name__ == "__main__":
    store_images()