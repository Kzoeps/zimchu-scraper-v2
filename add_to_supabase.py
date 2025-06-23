import traceback

from supabase_zimchu import supabase
from pandas import read_csv, isna
from apartment_class import Apartment
from pydash import omit_by
from json import loads
from scrape_constants import SCRAPED_FILE_NAME
from utils import setup_logging

# Set up logger
logger = setup_logging("zimchu-scraper-supabase")
existing_listing_ids = []
new_listings_added = 0


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


def get_rent(rent: int | None) -> int:
    if rent is None:
        return 0
    # when users list rent as 5.5 it is converted to 5500
    return rent * 1000 if rent < 10 else rent


def get_listing_payload(apartment: Apartment):
    listing_payload = {
        "id": apartment.id,
        "image_uris": apartment.uploaded_image_uris,
        "post_url": apartment.post_url,
        "created_at": apartment.creation_time,
        "size": apartment.size,
        "rent": get_rent(apartment.rent),
        "specific_location": apartment.specific_location,
        "phone_number": apartment.phone_number,
        "location": apartment.location,
        "post_hash": apartment.message_hash,
    }
    cleaned_payload = omit_by(listing_payload, lambda x: not x or isna(x))
    return cleaned_payload


def get_existing_listings():
    try:
        logger.info("Fetching existing listings from Supabase")
        response = supabase.table("listings_v2").select("id").execute()
        listing_ids = [d["id"] for d in response.data]
        logger.info(f"Found {len(listing_ids)} existing listings")
        return listing_ids
    except Exception as e:
        logger.error("Failed to get existing listings from Supabase")
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return []


def add_to_supabase(row: dict):
    try:
        print(f"\n =========LISTING ID {row.get('post_id', 'unknown')}=========\n")
        apartment = create_apartment(row)

        if str(apartment.id) in existing_listing_ids:
            logger.info(f"Listing with id {apartment.id} already exists, skipping")
            return

        logger.info(f"Uploading images for listing {apartment.id}")
        apartment.set_supabase_image_uris()

        logger.info(f"Extracting post text for listing {apartment.id}")
        apartment.extract_post_text()

        if not apartment.valid_post:
            logger.info(f"Listing {apartment.id} marked as invalid, skipping")
            return

        listing_payload = get_listing_payload(apartment)
        logger.info(f"Inserting listing with ID ({listing_payload['id']}) into Supabase.")

        response = supabase.table("listings_v2").insert(listing_payload).execute()
        logger.info(f"Successfully inserted listing with ID: {listing_payload['id']}")
        global new_listings_added
        new_listings_added += 1

        # Only log detailed response in debug mode
        logger.debug(f"Supabase response: {response}")
        print(response)
    except Exception as e:
        logger.error(f"Failed to insert listing: {str(e)}")
        logger.error(traceback.format_exc())
        print("Insertion failed")
        print(e)


def read_and_add_to_db(fileName: str):
    try:
        logger.info(f"Reading data from file: {fileName}")
        scraped_df = read_csv(fileName)
        global existing_listing_ids
        existing_listing_ids = get_existing_listings()
        logger.info(f"Found {len(scraped_df)} entries to process")

        # Process each row and add to Supabase
        scraped_df.apply(add_to_supabase, axis=1)
        logger.info("Completed processing all listings")
    except Exception as e:
        logger.error(f"Error reading or processing file {fileName}: {str(e)}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    logger.info(f"Starting standalone supabase import from {SCRAPED_FILE_NAME}")
    read_and_add_to_db(SCRAPED_FILE_NAME)
    logger.info("Standalone supabase import completed")
