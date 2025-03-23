import pandas as pd
import logging
import traceback
from hashlib import sha256

from test_extraction import TEST_EXTRACTION
from scrape_constants import SCRAPED_FILE_NAME
from utils import setup_logging

# Set up logger
logger = setup_logging("zimchu-scraper-data")

columns = [
    "post_id",
    "post_text",
    "image_uris",
    "poster_url",
    "post_url",
    "creation_time",
    "message_hash",
]
# Create a DataFrame with columns post_id, post_text, and image_uris
df = pd.DataFrame(columns=columns)

# Create an object with the following keys: post_id, post_text, and image_uris all of which are arrays

dataContainer = {
    "post_id": [],
    "post_text": [],
    "image_uris": [],
    "poster_url": [],
    "post_url": [],
    "creation_time": [],
    "message_hash": [],
}

"""
hashing the messages to see if there are any duplicates and going to use this in the db as well so as to avoid any duplicates
"""


def hash_message(message):
    content = message.encode("utf-8")
    sha256_hash = sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()


# Add scraped data to the data container
def add_to_data(post_id, post_message, image_uris, poster_url, post_url, creation_time):
    try:
        logger.info(f"Adding post with ID: {post_id} to data container")
        dataContainer["post_id"].append(post_id)
        dataContainer["post_text"].append(post_message)
        dataContainer["image_uris"].append(image_uris)
        dataContainer["poster_url"].append(poster_url)
        dataContainer["post_url"].append(post_url)
        dataContainer["creation_time"].append(creation_time)
        message_hash = hash_message(post_message)
        dataContainer["message_hash"].append(message_hash)
        
        logger.debug(f"Post details - ID: {post_id}, Creation time: {creation_time}, Images: {len(image_uris)}")
    except Exception as e:
        logger.error(f"Failed to add data for post ID: {post_id}")
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        print("adding to dataframe failed for post id", post_id)
        print(e)


# create a function to convert data to a dataframe
def data_to_df(data):
    return pd.DataFrame(data, columns=columns)


# create a function to drop rows with duplicate post_id's keeping just one
def drop_duplicates(df):
    return df.drop_duplicates(subset=["post_id"])


# Save the dataframe as CSV file
def save_as_csv(df):
    try:
        logger.info(f"Preparing to save data to CSV file: {SCRAPED_FILE_NAME}")
        
        # Clean up the dataframe
        df = clean_up(df)
        
        # Save to CSV
        df.to_csv(f"./{SCRAPED_FILE_NAME}", index=False)
        logger.info(f"Successfully saved {len(df)} rows to {SCRAPED_FILE_NAME}")
        print("saved csv files as:", SCRAPED_FILE_NAME)
    except Exception as e:
        logger.error(f"Failed to save CSV file: {str(e)}")
        logger.error(traceback.format_exc())
        raise


def save_data():
    try:
        logger.info("Converting collected data to dataframe")
        df = data_to_df(dataContainer)
        logger.info(f"Created dataframe with {len(df)} rows")
        
        # Save the dataframe
        save_as_csv(df)
    except Exception as e:
        logger.error(f"Failed to save data: {str(e)}")
        logger.error(traceback.format_exc())
        raise


def clean_up(df):
    logger.info(f"Cleaning up dataframe with {len(df)} rows")
    
    # Log initial row count
    initial_count = len(df)
    
    # Drop duplicates based on post_id
    df = df.drop_duplicates(subset=["post_id"])
    logger.info(f"After removing duplicate post_ids: {len(df)} rows")
    
    # Drop duplicates based on post_text
    df = df.drop_duplicates(subset=["post_text"])
    logger.info(f"After removing duplicate post_text: {len(df)} rows")
    
    # Drop duplicates based on message_hash
    df = df.drop_duplicates(subset=["message_hash"])
    logger.info(f"After removing duplicate message_hash: {len(df)} rows")
    
    # Drop rows with empty post_text
    df = df.dropna(subset=["post_text"])
    df = df[df["post_text"].str.strip() != ""]
    logger.info(f"After removing empty post_text: {len(df)} rows")
    
    # Log summary of cleanup
    removed = initial_count - len(df)
    logger.info(f"Cleanup complete: Removed {removed} duplicate/invalid rows ({removed/initial_count*100:.2f}%)")
    
    return df


if __name__ == "__main__":
    logger.info("Running scraped_data_saver in standalone mode with test extraction data")
    try:
        for idx, data in enumerate(TEST_EXTRACTION):
            logger.info(f"Processing test data item {idx+1}/{len(TEST_EXTRACTION)}")
            add_to_data(
                data["post_id"],
                data["post_message"],
                data["attachment_uris"],
                data["poster_url"],
                data["post_url"],
                data["creation_time"],
            )
        
        logger.info("Converting test data to dataframe")
        df = data_to_df(dataContainer)
        
        logger.info("Saving test data to CSV")
        save_as_csv(df)
        
        logger.info("Test data processing completed successfully")
    except Exception as e:
        logger.error(f"Error in test data processing: {str(e)}")
        logger.error(traceback.format_exc())
