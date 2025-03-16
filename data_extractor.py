from os import getenv
from re import search

from dotenv import load_dotenv
from openai import LengthFinishReasonError, OpenAI
from pydantic import BaseModel
from location_formatter import get_standard_location
from time import sleep

from prompt_constants import PROMPT

load_dotenv()
OPENAI_API_KEY: str = getenv("OPENAI_API_KEY")
openAiClient = OpenAI(api_key=OPENAI_API_KEY)

"""
TODOS:
1. Handle mutiple tries for the API since it sometimes fails
2. Add to supabase
    2.1 Add logic to check if the post is already in the database
        2.1.1 dont forget to check for the hash message as well
3. creation time is not present anymore so maybe dig through it or just make it automatic
"""


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


def sanitize(apartment: Apartment):
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


def extract_data(data) -> Apartment:
    retries = 3
    if not data:
        return
    for trial in range(retries):
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
                return apartment
            elif response.refusal:
                print("Refusal:", response.refusal)
                break
        except Exception as e:
            if type(e) == LengthFinishReasonError:
                print("Too many tokens", e)
            print(f"Parsing fail for: {data}")
            print("Reason:", e)
            delay = 1.5 * (trial + 1)
            print(f"Retrying in {delay} seconds")
            sleep(delay)
    return None


def get_structured_data(data) -> Apartment:
    apartment = extract_data(data)
    if apartment:
        return sanitize(apartment)
