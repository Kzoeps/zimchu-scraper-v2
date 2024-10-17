from pydantic import BaseModel
from openai import OpenAI
from prompt_constants import PROMPT
from pandas import DataFrame, read_csv
from dotenv import load_dotenv
from os import getenv

load_dotenv()
OPENAI_API_KEY: str = getenv("OPENAI_API_KEY")
openAiClient = OpenAI(api_key=OPENAI_API_KEY)

SCRAPED_FILE = "./scraped-data.csv"
scraped_df = read_csv(SCRAPED_FILE)


class Apartment(BaseModel):
    rent: int
    size: int
    phone_number: str
    location: str
    specific_location: str


def get_jsonified(data):
    if not data: return
    try:
        completion = openAiClient.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": data},
            ],
            response_format=Apartment,
        )
        apartment = completion.choices[0].message.parsed
        print(apartment)
        return apartment
    except Exception as e:
        print(f"Parsing fail for: {data}")
        print("Reason:", e)
        return None


scraped_df["post_text"].apply(get_jsonified)
