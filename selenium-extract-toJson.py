import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from extract_country_gpt import get_country
from helium import *
import platform

def remove_non_ascii_chars(text):
    return ''.join(char for char in text if ord(char) < 128)

# Fetch env variables
load_dotenv()
MARKLINES_USERNAME = os.getenv('MARKLINES_USERNAME')
MARKLINES_PASSWORD = os.getenv('MARKLINES_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if 'Windows'==platform.system():
    win=True
    
print(platform.system())

# Selenium setup ('Arch Linux')
chrome_options = Options()
chrome_options.add_experimental_option('detach', True) # keeps the window open after execution
#driver = webdriver.Chrome(options=chrome_options, service=Service('/home/Alan/chromedriver-linux64/chromedriver'))
driver=start_chrome(headless=False)
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


# Dictionary for the current part which will be written to a json file
part_dict = {'buyer':{}, 'supplier':{}}


# Open the link of the part to be scraped
# Future scope -> iterate through links dynamically or read them from a file
part_link = 'https://www.marklines.com/en/wsw/axle/'
part_name = 'Axle'
driver.get(part_link)
print('Navigated to part link')

WebDriverWait(driver,5)

# Fetch table using beautiful soup 
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')
#soup.encode('utf-8')
table = soup.find('table', id='market_share_data').find('tbody')
# Fetch relevant data from each row and add to part_dict
rows = table.find_all('tr')
for row in rows[:]:
    tds = row.find_all('td')
    try:
        supplier_link = 'https://www.marklines.com/' + tds[4].find('a')['href']
    except:
        supplier_link = None
    tds = [td.get_text().strip() for td in tds]
    region, buyer, supplier, specific_part = tds[0], tds[1], tds[4], tds[5]
    
    #------------------------------------------------------------------------------------
    #essential for Windows
    if(win):
        region=remove_non_ascii_chars(region)
        buyer=remove_non_ascii_chars(buyer)
        supplier=remove_non_ascii_chars(supplier)
        specific_part=remove_non_ascii_chars(specific_part)
    #------------------------------------------------------------------------------------
    
    
    if buyer not in part_dict['buyer']:
        part_dict['buyer'][buyer] = 1
    else:
        part_dict['buyer'][buyer] += 1
    if supplier not in part_dict['supplier']:
        part_dict['supplier'][supplier] = 1
    else:
        part_dict['supplier'][supplier] += 1

    # Update/Create buyer.json
    if os.path.exists(f'TempJSONs/Buyers/{buyer}.json'):
        with open(f'TempJSONs/Buyers/{buyer}.json', 'r') as file:
            buyer_dict = json.load(file)
    else:
        buyer_dict = {'region':region, 'parts-bought':{}, 'specific-parts-bought':{}, 'suppliers':{}}
    if str(supplier)+":"+str(part_name) not in buyer_dict['suppliers']:
        buyer_dict['suppliers'][str(supplier)+":"+str(part_name)] = 1
    else:
        buyer_dict['suppliers'][str(supplier)+":"+str(part_name)] += 1
    if specific_part not in buyer_dict['specific-parts-bought']:
        buyer_dict['specific-parts-bought'][specific_part] = 1
    else:
        buyer_dict['specific-parts-bought'][specific_part] += 1
    if part_name not in buyer_dict['parts-bought']:
        buyer_dict['parts-bought'][part_name] = 1
    else:
        buyer_dict['parts-bought'][part_name] += 1
    with open(f'TempJSONs/Buyers/{buyer}.json', 'w') as file:
        json.dump(buyer_dict, file, ensure_ascii=False, indent=4)

    # Update/Create supplier.json
    if os.path.exists(f'TempJSONs/Suppliers/{supplier}.json'):
        with open(f'TempJSONs/Suppliers/{supplier}.json', 'r') as file:
            supplier_dict = json.load(file)
    elif supplier_link and 'top500' in supplier_link:
        print(supplier)
        supplier_dict = {'top500':True, 'parts_sold':{}, 'specific_parts_sold':{}, 'buyers':{}}
        driver.get(supplier_link)
        
        #-------------------------------
        #Comment for better performance
        WebDriverWait(driver,5)
        #-------------------------------

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        company_profile = soup.find('div', class_='over-view')
        p_tags = company_profile.find_all('p')
        if win:
            info = [remove_non_ascii_chars(p.get_text().strip()) for p in p_tags]
        else:
            info = [p.get_text().strip() for p in p_tags]
        for i in range(len(info)):
            if not info[i][0].isalpha():
                info[i] = info[i][1:]
        for i in range(0, len(info) - 1, 2):
            supplier_dict[info[i]] = info[i + 1]
            
        if win:
            address = remove_non_ascii_chars(company_profile.find_all('div')[-1].get_text().strip())
        else:
            address=company_profile.find_all('div')[-1].get_text().strip()
        supplier_dict[info[len(info) - 1]] = address
        supplier_dict['Country'] = get_country(address)
    elif supplier_link:
        print(supplier)
        supplier_dict = {'top500':False, 'parts_sold':{}, 'specific_parts_sold':{}, 'buyers':{}}
        driver.get(supplier_link)
        
        #-------------------------------
        #Comment for better performance
        WebDriverWait(driver,5)
        #-------------------------------
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        info_table = soup.find('div', id='basic-info').find('tbody')
        info_headers = info_table.find_all('th')
        info_headers = [th.get_text().strip() for th in info_headers]
        info_data = info_table.find_all('td')
        if win:
            info_data = [remove_non_ascii_chars(td.get_text().strip()) for td in info_data]
        else:
            info_data = [td.get_text().strip() for td in info_data]
        for i in range(len(info_headers)):
            supplier_dict[info_headers[i]] = info_data[i]

    if part_name not in supplier_dict['parts_sold']:
        supplier_dict['parts_sold'][part_name] = 1
    else:
        supplier_dict['parts_sold'][part_name] += 1
    if str(buyer)+":"+str(part_name) not in supplier_dict['buyers']:
        supplier_dict['buyers'][str(buyer)+":"+str(part_name)] = 1
    else:
        supplier_dict['buyers'][str(buyer)+":"+str(part_name)] += 1
    if specific_part not in supplier_dict['specific_parts_sold']:
        supplier_dict['specific_parts_sold'][specific_part] = 1
    else:
        supplier_dict['specific_parts_sold'][specific_part] += 1
    with open(f'TempJSONs/Suppliers/{supplier}.json', 'w') as file:
        json.dump(supplier_dict, file, ensure_ascii=False, indent=4)


# Write the part dictionary to a json
with open(f'TempJSONs/Parts/{part_name}.json', 'w') as file:
    json.dump(part_dict, file, ensure_ascii=False, indent=4)
print("Part file created")



# driver.quit()

