import pandas as pd
from typing import Dict, List
from hashlib import sha256

from test_extraction import TEST_EXTRACTION

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
def add_to_data(id, text, uri, poster_url, post_url, creation_time):
    dataContainer["post_id"].append(id)
    dataContainer["post_text"].append(text)
    dataContainer["image_uris"].append(uri)
    dataContainer["poster_url"].append(poster_url)
    dataContainer["post_url"].append(post_url)
    dataContainer["creation_time"].append(creation_time)
    dataContainer["message_hash"].append(hash_message(text))


# create a function to convert data to a dataframe
def data_to_df(data):
    return pd.DataFrame(data, columns=columns)


# create a function to drop rows with duplicate post_id's keeping just one
def drop_duplicates(df):
    return df.drop_duplicates(subset=["post_id"])


#  create a function to save the df as csv
def save_df(df):
    df = clean_up(df)
    df.to_csv(f"./scraped-data.csv", index=False)


def clean_up(df):
    df = df.drop_duplicates(subset=["post_id"])
    df = df.drop_duplicates(subset=["post_text"])
    df = df.drop_duplicates(subset=["message_hash"])
    df = df.dropna(subset=["post_text"])
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
    df = clean_up(df)
    save_df(df)
