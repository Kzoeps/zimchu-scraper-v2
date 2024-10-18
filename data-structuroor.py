from os import getenv
from re import search

from dotenv import load_dotenv
from openai import LengthFinishReasonError, OpenAI
from pandas import DataFrame, read_csv
from pydantic import BaseModel
from location_formatter import get_standard_location

from prompt_constants import PROMPT

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


"""
sometimes the number that chatgpt outputs is ":[]", especially for postings which are not rental listings.(searching for apartments, etc)
using regex to filter if there are 3 or more digits and if so then return the number
"""


def standardize_location(apartment: Apartment):
    if apartment.location.strip():
        apartment.location = get_standard_location(apartment.location)


def clean_phone_number(apartment: Apartment):
    if not search(r"\d{4,}", apartment.phone_number):
        apartment.phone_number = ""


def get_jsonified(apartment: Apartment):
    clean_phone_number(apartment)
    if (
        apartment.rent == 0
        and apartment.size == 0
        and apartment.phone_number == ""
        and apartment.location == ""
        and apartment.specific_location == ""
    ):
        return None
    if apartment.size >= 6:
        return None
    standardize_location(apartment)
    return apartment


def get_structued_data(data):
    if not data:
        return
    try:
        completion = openAiClient.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": data},
            ],
            response_format=Apartment,
        )
        response = completion.choices[0].message
        apartment = response.parsed
        if apartment:
            print(apartment.model_dump_json())
            return apartment.model_dump_json()
        elif response.refusal:
            print("Refusal:", response.refusal)
            return None
    except Exception as e:
        if type(e) == LengthFinishReasonError:
            print("Too many tokens", e)
        print(f"Parsing fail for: {data}")
        print("Reason:", e)
        return None


# scraped_df["structured"] = scraped_df["post_text"].apply(get_jsonified)
# scraped_df.to_csv("structured-data.csv", index=False)
print(
    get_jsonified(
        Apartment(
            phone_number="23[]2392",
            rent=0,
            size=0,
            location="bibesa",
            specific_location="",
        )
    )
)
