import pandas as pd
from hashlib import sha256

from test_extraction import TEST_EXTRACTION
from scrape_constants import SCRAPED_FILE_NAME

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


# Create a function which has three parameters: id, text and uri and appends them to the data object
def add_to_data(post_id, post_message, image_uris, poster_url, post_url, creation_time):
    try:
        dataContainer["post_id"].append(post_id)
        dataContainer["post_text"].append(post_message)
        dataContainer["image_uris"].append(image_uris)
        dataContainer["poster_url"].append(poster_url)
        dataContainer["post_url"].append(post_url)
        dataContainer["creation_time"].append(creation_time)
        dataContainer["message_hash"].append(hash_message(post_message))
    except Exception as e:
        print("adding to dataframe failed for post id", post_id)
        print(e)


# create a function to convert data to a dataframe
def data_to_df(data):
    return pd.DataFrame(data, columns=columns)


# create a function to drop rows with duplicate post_id's keeping just one
def drop_duplicates(df):
    return df.drop_duplicates(subset=["post_id"])


#  create a function to save the df as csv
def save_as_csv(df):
    df = clean_up(df)
    df.to_csv(f"./{SCRAPED_FILE_NAME}", index=False)
    print("saved csv files as:", SCRAPED_FILE_NAME)


def save_data():
    df = data_to_df(dataContainer)
    save_as_csv(df)


def clean_up(df):
    df = df.drop_duplicates(subset=["post_id"])
    df = df.drop_duplicates(subset=["post_text"])
    df = df.drop_duplicates(subset=["message_hash"])
    df = df.dropna(subset=["post_text"])
    df = df[df["post_text"].str.strip() != ""]
    return df


if __name__ == "__main__":
    for data in TEST_EXTRACTION:
        add_to_data(
            data["post_id"],
            data["post_message"],
            data["attachment_uris"],
            data["poster_url"],
            data["post_url"],
            data["creation_time"],
        )
    df = data_to_df(dataContainer)
    save_as_csv(df)
