import logging
import traceback

from supabase_zimchu import supabase
from pandas import read_csv, isna
from apartment_class import Apartment
from pydash import omit_by
from json import loads
from scrape_constants import SCRAPED_FILE_NAME
from utils import print_demarkers, setup_logging

# Set up logger
logger = setup_logging("zimchu-scraper-supabase")


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
        logger.info(f"Processing listing from post ID: {row.get('post_id', 'unknown')}")
        existing_listings = get_existing_listings()
        apartment = create_apartment(row)
        
        if str(apartment.id) in existing_listings:
            logger.info(f"Listing with id {apartment.id} already exists, skipping")
            return
            
        logger.info(f"Uploading images for listing {apartment.id}")
        print("\n =========UPLOAD IMAGES=========\n")
        apartment.set_supabase_image_uris()
        
        logger.info(f"Extracting post text for listing {apartment.id}")
        print("\n =========EXTRACT POST TEXT=========\n")
        apartment.extract_post_text()
        
        if not apartment.valid_post:
            logger.info(f"Listing {apartment.id} marked as invalid, skipping")
            return
            
        listing_payload = get_listing_payload(apartment)
        logger.info(f"Inserting listing into Supabase with ID: {listing_payload['id']}")
        print("\n =========INSERTING LISTING=========\n")
        print("inserting listing with id:", listing_payload["id"])
        
        response = supabase.table("listings_v2").insert(listing_payload).execute()
        logger.info(f"Successfully inserted listing {listing_payload['id']}")
        
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