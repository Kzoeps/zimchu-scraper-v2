import os
from dotenv import load_dotenv
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from supabase_zimchu import supabase
from time import sleep
from supabase import StorageException


load_dotenv()
storage_url: str = os.getenv("SUPABASE_STORAGE_URL")


def get_bucket_path(post_id, image_id):
    return f"{post_id}/{image_id}"


def create_uri(post_id, image_id):
    return f"{storage_url}/{get_bucket_path(post_id, image_id)}"


def get_image_from_fb(image_uri, path):
    if image_uri == "nan":
        return None
    print(f"getting image from fb for {path}")
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = Session()
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    try:
        response = session.get(image_uri)
        response.raise_for_status()
        return bytes(response.content)
    except Exception as e:
        error = f"Error getting image: {e}"
        return None


def upload_image(image_uri, path):
    retries = 3
    image = get_image_from_fb(image_uri, path)
    if image:
        for attempt in range(retries):
            try:
                print(f"uploading image to {path}; attempt {attempt + 1}")
                response = supabase.storage.from_("listings_v2").upload(
                    path=path, file=image, file_options={"content-type": "image/png"}
                )
                if response.status_code == 200:
                    print(f"uploaded image to {path}")
                    return path
                elif response.status_code == 400:
                    print(
                        f"upload failed with status code: {response.status_code}; Error: {response.content}"
                    )
                    return
                else:
                    raise Exception(
                        f"Supabase upload failed with status code: {response.status_code}; Error: {response.content}"
                    )
            except StorageException as e:
                print(f"Error uploading image: {e}")
                delay = 1.5 * (attempt + 1)
                print(f"retrying in {delay} seconds")
                sleep(delay)


def get_image_link(uploaded_uri):
    return f"{storage_url}/{uploaded_uri}"


def upload_images(image_uris, post_id):
    image_links = []
    for i, image_uri in enumerate(image_uris):
        path = get_bucket_path(post_id, i + 2)
        uploaded_uri = upload_image(image_uri, path)
        if uploaded_uri:
            image_links.append(get_image_link(uploaded_uri))
    return image_links


test_image_uris = [
    "https://scontent.fijd1-1.fna.fbcdn.net/v/t39.30808-6/462764375_3822099021400526_7600732096871187156_n.jpg?stp=cp6_dst-jpg&_nc_cat=109&ccb=1-7&_nc_sid=aa7b47&_nc_ohc=GZblfQNHk8sQ7kNvgFctEyd&_nc_zt=23&_nc_ht=scontent.fijd1-1.fna&_nc_gid=A87kpU5VvoA1sAiDk2m1RbP&oh=00_AYDKxu1X-EPO8A26IcI8gDQaOwxB7-_OamxRAUhU2uRLCg&oe=6719F3EA"
]
