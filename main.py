import os
import re
import time
import json
import traceback
import seleniumwire.undetected_chromedriver as uc

from random import randint
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.utils import decode

from facebook_response_mappers import (
    get_attachments,
    get_date_of_posting,
    get_post_id,
    get_post_message,
    get_post_url,
    get_poster_url,
)

from add_to_supabase import read_and_add_to_db
from scraped_data_saver import add_to_data, save_data
from scrape_constants import FACEBOOK_GROUP_URL, SCRAPED_FILE_NAME
from utils import print_demarkers, setup_logging

# Rent a House in Thimphu Bhutan 91k members group

# Initialize logger
logger = setup_logging()

# Log script start with timestamp for cron job tracking
start_time = datetime.now()
logger.info(f"=========== ZIMCHU SCRAPER STARTED AT {start_time} ===========")

sleep_time = randint(1, 10)
logger.info(f"Generated random sleep time: {sleep_time} seconds")

logger.info("Loading environment variables")
load_dotenv()
facebook_username: str = os.getenv("FACEBOOK_USERNAME")
facebook_password: str = os.getenv("FACEBOOK_PASSWORD")
run_headless: bool = os.getenv("RUN_HEADLESS", False) == "True"
logger.info(f"Environment variables loaded successfully")
logger.info(f"Running in headless mode: {run_headless}")
print_demarkers("ENV keys loaded")


logger.info("Setting up Chrome Options")
# Chrome Options
chrome_options = uc.ChromeOptions()
if run_headless:
    logger.info("Running in headless mode")
    chrome_options.add_argument("--headless")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--accept-insecure-certs")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-extensions")
logger.info("Chrome Options set!")


# ## Create Chrome Driver
logger.info("Setting up Chrome driver")
try:
    driver = uc.Chrome(options=chrome_options, seleniumwire_options={})
    logger.info("Chrome driver initialized successfully")
    print_demarkers("Selenium is ready")
except Exception as e:
    logger.error(f"Failed to initialize Chrome driver: {str(e)}")
    logger.error(traceback.format_exc())
    raise

facebook_url = "https://www.facebook.com"
logger.info("Opening Facebook main page")
try:
    driver.get(facebook_url)
    logger.info(f"Facebook opened, waiting for {sleep_time} seconds")
    time.sleep(sleep_time)
except Exception as e:
    logger.error(f"Failed to open Facebook: {str(e)}")
    logger.error(traceback.format_exc())
    driver.quit()
    raise


def login():
    logger.info("Attempting to login to Facebook")
    try:
        username = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "pass")
        
        logger.info("Entering username")
        username.send_keys(facebook_username)
        time.sleep(randint(4, 9))
        
        logger.info("Entering password")
        password.send_keys(facebook_password)
        time.sleep(randint(3, 7))
        
        logger.info("Submitting login form")
        password.send_keys(Keys.RETURN)
        
        sleep_time = randint(1, 10)
        logger.info(f"Login form submitted, waiting for {sleep_time} seconds")
        time.sleep(sleep_time)
        
        logger.info("Waiting for presence of role banner CSS selector (login confirmation)")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[role="banner"]'))
        )
        logger.info("Login successful - banner element found")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        logger.error(traceback.format_exc())
        driver.quit()
        raise

def save_cookies():
    with open("cookies.json", "w") as f:
        json.dump(driver.get_cookies(), f)

def load_cookies():
    if not os.path.exists("cookies.json"):
        logger.warning("Cookie file not found")
        return None
    with open("cookies.json", "r") as f:
        cookie = json.load(f)
        return cookie

def feed_response_interceptor(request, response):
    if (
        request.url.startswith("https://www.facebook.com/api/graphql/")
        and request.method == "POST"
    ):
        if response.headers.get("content-type") == 'text/html; charset="utf-8"':
            logger.info(f"Intercepted response from: {request.url}")
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
                        
                        # Log the extracted data
                        logger.info(f"Found post: {post_id} from {creation_time}")
                        logger.debug(
                            f"Post details: ID={post_id}, URL={post_url}, "
                            f"Poster={poster_url}, Images={len(attachment_uris)}, "
                            f"CreationTime={creation_time}"
                        )
                        
                        # Add the data to our data structure
                        add_to_data(
                            post_id=post_id,
                            post_message=post_message,
                            image_uris=attachment_uris,
                            poster_url=poster_url,
                            post_url=post_url,
                            creation_time=creation_time,
                        )
            except Exception as e:
                logger.error(f"Error parsing response: {str(e)}")
                logger.error(traceback.format_exc())


try:
    login()
    save_cookies()
    print_demarkers("login successful")
    logger.info(f"Navigating to Facebook group: {FACEBOOK_GROUP_URL}")
    
    driver.get(FACEBOOK_GROUP_URL)
    logger.info("Setting up response interceptor")
    driver.response_interceptor = feed_response_interceptor
    
    initial_wait = 10
    logger.info(f"Waiting {initial_wait} seconds for page to load completely")
    time.sleep(initial_wait)
    
    logger.info("Starting page scrolling to load more content")
    for scroll_num in range(10):
        scroll_wait = randint(3, 9)
        logger.info(f"Scroll #{scroll_num+1}/10, waiting {scroll_wait} seconds")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_wait)
    
    logger.info("Scrolling completed")
except Exception as e:
    logger.error(f"Error during Facebook navigation/scrolling: {str(e)}")
    logger.error(traceback.format_exc())
    driver.quit()
    raise

print_demarkers("Scraping done")
logger.info("Facebook scraping completed")

try:
    logger.info("Saving scraped data to file")
    save_data()
    logger.info(f"Data saved successfully to {SCRAPED_FILE_NAME}")
    print_demarkers(f"saved data to {SCRAPED_FILE_NAME}")
    
    logger.info("Closing browser")
    driver.quit()
    logger.info("Browser closed successfully")
    
    logger.info("Beginning upload to Supabase")
    print_demarkers("Adding data to supabase")
    read_and_add_to_db(SCRAPED_FILE_NAME)
    logger.info("Data successfully added to Supabase")
    print_demarkers("Added to db")
    
    # Log completion with runtime
    end_time = datetime.now()
    run_duration = end_time - start_time
    logger.info(f"=========== ZIMCHU SCRAPER COMPLETED AT {end_time} ===========")
    logger.info(f"Total runtime: {run_duration}")
except Exception as e:
    logger.error(f"Error in final processing steps: {str(e)}")
    logger.error(traceback.format_exc())
    # Still try to close the browser if it's open
    try:
        driver.quit()
    except:
        pass
    raise
