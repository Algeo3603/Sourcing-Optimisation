import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Fetch credentials
MARKLINES_USERNAME = os.getenv('MARKLINES_USERNAME')
MARKLINES_PASSWORD = os.getenv('MARKLINES_PASSWORD')

# Selenium setup ('Arch Linux')
chrome_options = Options()
chrome_options.add_experimental_option("detach", True) # keeps the window open after execution
driver = webdriver.Chrome(options=chrome_options, service=Service('/home/Alan/chromedriver-linux64/chromedriver'))
print("Selenium is ready")

# Open marklines and login
driver.get('https://www.marklines.com/en/members/login')
driver.maximize_window()
username_field = driver.find_element(By.NAME,"profiles.login.login_id")  
password_field = driver.find_element(By.NAME,"profiles.login.password")
login_button = driver.find_element(By.ID,"login_btn")  
username_field.send_keys(MARKLINES_USERNAME)
password_field.send_keys(MARKLINES_PASSWORD)
# login_button.click()
print("Logged in to MarkLines")

# Navigate to '300 Components' page
# driver.get("www.google.com")
main_window = driver.current_window_handle
print(main_window)
driver.switch_to.new_window('tab')
driver.get("https://www.google.com/")
time.sleep(3)
driver.close()
driver.switch_to.window(main_window)
time.sleep(3)
driver.close()


# driver.quit()