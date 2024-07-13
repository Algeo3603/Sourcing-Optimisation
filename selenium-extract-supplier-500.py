import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import json


# Fetch env variables
load_dotenv()
MARKLINES_USERNAME = os.getenv('MARKLINES_USERNAME')
MARKLINES_PASSWORD = os.getenv('MARKLINES_PASSWORD')


# Selenium setup ('Arch Linux')
chrome_options = Options()
chrome_options.add_experimental_option('detach', True) # keeps the window open after execution
driver = webdriver.Chrome(options=chrome_options, service=Service('/home/Alan/chromedriver-linux64/chromedriver'))
print('Selenium is ready')


# Open marklines and login
driver.get('https://www.marklines.com/en/members/login')
driver.maximize_window()
username_field = driver.find_element(By.NAME,'profiles.login.login_id')  
password_field = driver.find_element(By.NAME,'profiles.login.password')
login_button = driver.find_element(By.ID,'login_btn')  
username_field.send_keys(MARKLINES_USERNAME)
password_field.send_keys(MARKLINES_PASSWORD)
login_button.click()
print('Logged in to MarkLines')

# Scrape supplier
supplier_link = 'https://www.marklines.com/en/top500/continental/'

if 'top500' in supplier_link:
    driver.get(supplier_link)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    company_profile = soup.find('div', class_='over-view')
    p_tags = company_profile.find_all('p')
    info = [p.get_text().strip() for p in p_tags]
    for i in range(len(info)):
        if not info[i][0].isalpha():
            info[i] = info[i][1:]
    supplier_dict = {'top500':True, 'parts_sold':[], 'specific_parts_sold':[], 'buyers':[]}
    for i in range(0, len(info) - 1, 2):
        print(i, info[i], info[i+1])
        supplier_dict[info[i]] = info[i + 1]
    address = soup.find_all('div')[-1].get_text().strip()
    supplier_dict[info[len(info) - 1]] = address
    print(supplier_dict)
