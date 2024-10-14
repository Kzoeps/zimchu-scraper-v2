import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import time

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
print("Facebook opened, waiting for random seconds")
time.sleep(10)

# LOGIN TO FACEBOOK
print("getting env keys")
load_dotenv()
facebook_username = os.getenv("FACEBOOK_USERNAME")
facebook_password = os.getenv("FACEBOOK_PASSWORD")
print("env keys set")


print("logging into facebook")
username = driver.find_element(By.ID, "email")
password = driver.find_element(By.ID, "pass")

username.send_keys(facebook_username)
password.send_keys(facebook_password)

# password.send_keys(Keys.RETURN)

time.sleep(4)
driver.quit()
