import json
from data_structuroor import get_structured_data


class Apartment:
    # size: int
    # rent: int
    # phone_number: str
    # location: str
    # specific_location: str
    # valid_post: bool = True

    def __init__(
        self,
        id: str,
        post_text: str,
        image_uris: list[str],
        poster_url: str,
        post_url: str,
        creation_time: str,
        message_hash: str,
        size: int = None,
        rent: int = None,
        phone_number: str = None,
        location: str = None,
        specific_location: str = None,
        valid_post: bool = True,
    ):
        self.id = id
        self.post_text = post_text
        self.image_uris = image_uris
        self.poster_url = poster_url
        self.post_url = post_url
        self.creation_time = creation_time
        self.message_hash = message_hash
        self.size = size
        self.rent = rent
        self.phone_number = phone_number
        self.location = location
        self.specific_location = specific_location
        self.valid_post = valid_post

    def __repr__(self):
        return f"Apartment(id={self.id}, post_text={self.post_text}, image_uris={self.image_uris}, poster_url={self.poster_url}, post_url={self.post_url}, creation_time={self.creation_time}, message_hash={self.message_hash})"

    def display(self):
        """
        Method to print the apartment's details in a readable format.
        """
        print(f"Apartment ID: {self.id}")
        print(f"Post Text: {self.post_text}")
        print(f"Image URIs: {', '.join(self.image_uris)}")
        print(f"Poster URL: {self.poster_url}")
        print(f"Post URL: {self.post_url}")
        print(f"Creation Time: {self.creation_time}")
        print(f"Message Hash: {self.message_hash}")

    def extract_post_text(self):
        apartment_info = get_structured_data(self.post_text)
        if apartment_info == None:
            self.valid_post = False
            return None
        self.size = apartment_info.size
        self.rent = apartment_info.rent
        self.phone_number = apartment_info.phone_number
        self.location = apartment_info.location
        self.specific_location = apartment_info.specific_location
        return apartment_info

    def to_dict(self):
        """
        Method to convert the apartment object to a dictionary.
        """
        return {
            "id": self.id,
            "post_text": self.post_text,
            "image_uris": self.image_uris,
            "poster_url": self.poster_url,
            "post_url": self.post_url,
            "creation_time": self.creation_time,
            "size": self.size,
            "rent": self.rent,
            "phone_number": self.phone_number,
            "location": self.location,
            "message_hash": self.message_hash,
        }
