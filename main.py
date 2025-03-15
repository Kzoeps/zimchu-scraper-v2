import os
import re
import time
import json
from random import randint

import seleniumwire.undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.utils import decode

from extractors import (get_attachments, get_date_of_posting, get_post_id,
                         get_post_message, get_post_url, get_poster_url)

# Rent a House in Thimphu Bhutan 91k members group

sleep_time = randint(1, 10)
FACEBOOK_GROUP_URL = (
    "https://www.facebook.com/groups/1150322371661229?sorting_setting=CHRONOLOGICAL"
)
print("getting env keys")
load_dotenv()
facebook_username: str = os.getenv("FACEBOOK_USERNAME")
facebook_password: str = os.getenv("FACEBOOK_PASSWORD")
print("env keys set")


print("Setting up Chrome Options")
## Chrome Options
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--accept-insecure-certs")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-extensions")
print("Chrome Options set!")


## Create Chrome Driver
print("setting up driver")
driver = uc.Chrome(options=chrome_options, seleniumwire_options={})
print("Driver set!")

facebook_url = "https://www.facebook.com"
print("Opening Facebook")
driver.get(facebook_url)
print(f"Facebook opened, waiting for {sleep_time} seconds")
time.sleep(sleep_time)


def login():
    # LOGIN TO FACEBOOK
    print("logging into facebook")
    username = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "pass")

    username.send_keys(facebook_username)
    sleep_time = randint(1, 3)
    password.send_keys(facebook_password)
    sleep_time = randint(1, 3)

    password.send_keys(Keys.RETURN)

    sleep_time = randint(1, 10)
    print(f"logged into facebook, waiting for {sleep_time} seconds")
    time.sleep(sleep_time)

    print("waiting for presence of role banner css selector")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[role="banner"]'))
    )
    print("role banner css selector found")


def feed_response_interceptor(request, response):
    if (
        request.url.startswith("https://www.facebook.com/api/graphql/")
        and request.method == "POST"
    ):
        if response.headers.get("content-type") == 'text/html; charset="utf-8"':
            print("Intercepted response of", request.url)
            try:
                data = decode(
                    response.body, response.headers.get("Content-Encoding", "identity")
                )
                data = data.decode("utf-8")
                for line in data.splitlines():
                    data_expression = r'"data":{"node":.*}'
                    match = re.search(data_expression, line)
                    if match:
                        json_data = json.loads(line)
                        post_id = get_post_id(json_data)
                        post_message = get_post_message(json_data)
                        post_url = get_post_url(json_data)
                        poster_url = get_poster_url(json_data)
                        attachment_uris = get_attachments(json_data)
                        creation_time = get_date_of_posting(json_data)
                        print(
                            {
                                "post_id": post_id,
                                "post_message": post_message,
                                "post_url": post_url,
                                "poster_url": poster_url,
                                "attachment_uris": attachment_uris,
                                "creation_time": creation_time,
                            }
                        )
            except Exception as e:
                print("Error parsing response", e)


# login()
# driver.get(FACEBOOK_GROUP_URL)
driver.get("https://google.com")
# driver.response_interceptor = feed_response_interceptor
time.sleep(10)

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(randint(3, 8))


driver.quit()
