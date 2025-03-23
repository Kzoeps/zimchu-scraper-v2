from supabase_zimchu import supabase
from pandas import read_csv, isna
from apartment_class import Apartment
from pydash import omit_by
from json import loads
from scrape_constants import SCRAPED_FILE_NAME
from utils import print_demarkers


class Listing:
    id: str
    image_uris: list[str]
    created_at: str
    size: int
    rent: int
    specific_location: str
    location: str
    user_id: str
    phone_number: str
    post_url: str
    post_hash: str


def create_apartment(row):
    image_uris_list = row["image_uris"].replace("'", '"')
    image_uris_list = loads(image_uris_list)
    apartment = Apartment(
        id=row["post_id"],
        post_text=row["post_text"],
        image_uris=image_uris_list,
        poster_url=row["poster_url"],
        post_url=row["post_url"],
        creation_time=row["creation_time"],
        message_hash=row["message_hash"],
    )
    return apartment


def get_listing_payload(apartment: Apartment):
    listing_payload = {
        "id": apartment.id,
        "image_uris": apartment.uploaded_image_uris,
        "post_url": apartment.post_url,
        "created_at": apartment.creation_time,
        "size": apartment.size,
        "rent": apartment.rent,
        "specific_location": apartment.specific_location,
        "phone_number": apartment.phone_number,
        "location": apartment.location,
        "post_hash": apartment.message_hash,
    }
    cleaned_payload = omit_by(listing_payload, lambda x: not x or isna(x))
    return cleaned_payload


def get_existing_listings():
    try:
        response = supabase.table("listings_v2").select("id").execute()
        # convert id into in
        return [d["id"] for d in response.data]
    except Exception as e:
        print("Failed to get existing listings")
        print(e)
        return []

def add_to_supabase(row: dict):
    try:
        existing_listings = get_existing_listings()
        apartment = create_apartment(row)
        if str(apartment.id) in existing_listings:
            print(f"Listing with id {apartment.id} already exists")
            return
        print("\n =========UPLOAD IMAGES=========\n")
        apartment.set_supabase_image_uris()
        print("\n =========EXTRACT POST TEXT=========\n")
        apartment.extract_post_text()
        if not apartment.valid_post:
            return
        listing_payload = get_listing_payload(apartment)
        print("\n =========INSERTING LISTING=========\n")
        print("inserting listing with id:", listing_payload["id"])
        response = supabase.table("listings_v2").insert(listing_payload).execute()
        print(response)
    except Exception as e:
        print("Insertion failed")
        print(e)


def read_and_add_to_db(fileName: str):
    scraped_df = read_csv(fileName)
    scraped_df.apply(add_to_supabase, axis=1)

if __name__ == "__main__":
    read_and_add_to_db(SCRAPED_FILE_NAME)