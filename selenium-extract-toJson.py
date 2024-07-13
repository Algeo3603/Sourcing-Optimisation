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


# Dictionary for the current part which will be written to a json file
part_dict = {'buyer':set(), 'supplier':set()}


# Open the link of the part to be scraped
# Future scope -> iterate through links dynamically or read them from a file
part_link = 'https://www.marklines.com/en/wsw/wiring-harness/'
part_name = 'Wiring Harness'
driver.get(part_link)
print('Navigated to part link')


# Fetch table using beautiful soup 
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('table', id='market_share_data').find('tbody')
# Fetch relevant data from each row and add to part_dict
rows = table.find_all('tr')
for row in rows[:]:
    tds = row.find_all('td')
    supplier_link = 'https://www.marklines.com/' + tds[4].find('a')['href']
    tds = [td.get_text().strip() for td in tds]
    buyer, supplier, specific_part = tds[1], tds[4], tds[5]
    part_dict['buyer'].add(buyer)
    part_dict['supplier'].add(supplier)
    
    # Update/Create buyer.json
    if os.path.exists(f'TempJSONs/Buyers/{buyer}.json'):
        with open(f'TempJSONs/Buyers/{buyer}.json', 'r') as file:
            buyer_dict = json.load(file)
    else:
        buyer_dict = {'parts-bought':[], 'specific-parts-bought':[], 'suppliers':[]}
    if supplier not in buyer_dict['suppliers']:
        buyer_dict['suppliers'].append(supplier)
    if specific_part not in buyer_dict['specific-parts-bought']:
        buyer_dict['specific-parts-bought'].append(specific_part)
    if part_name not in buyer_dict['parts-bought']:
        buyer_dict['parts-bought'].append(part_name)
    with open(f'TempJSONs/Buyers/{buyer}.json', 'w') as file:
        json.dump(buyer_dict, file, ensure_ascii=False, indent=4)

    # Update/Create supplier.json
    if 'top500' in supplier_link:
        if os.path.exists(f'TempJSONs/Suppliers/{supplier}.json'):
            with open(f'TempJSONs/Suppliers/{supplier}.json', 'r') as file:
                supplier_dict = json.load(file)
        else:
            print(supplier)
            supplier_dict = {'top500':True, 'parts_sold':[], 'specific_parts_sold':[], 'buyers':[]}
            main_window = driver.current_window_handle
            driver.switch_to.new_window('tab')
            driver.get(supplier_link)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            company_profile = soup.find('div', class_='over-view')
            p_tags = company_profile.find_all('p')
            info = [p.get_text().strip() for p in p_tags]
            for i in range(len(info)):
                if not info[i][0].isalpha():
                    info[i] = info[i][1:]
            for i in range(0, len(info) - 1, 2):
                supplier_dict[info[i]] = info[i + 1]
            address = soup.find_all('div')[-1].get_text().strip()
            supplier_dict[info[len(info) - 1]] = address
            driver.close()
            driver.switch_to.window(main_window)
        if part_name not in supplier_dict['parts_sold']:
            supplier_dict['parts_sold'].append(part_name)
        if buyer not in supplier_dict['buyers']:
            supplier_dict['buyers'].append(buyer)
        if specific_part not in supplier_dict['specific_parts_sold']:
            supplier_dict['specific_parts_sold'].append(specific_part)    
        with open(f'TempJSONs/Suppliers/{supplier}.json', 'w') as file:
            json.dump(supplier_dict, file, ensure_ascii=False, indent=4)
    # print('.', end='') # To see progress in terminal as the script runs
# print()


# Write the part dictionary to a json
part_dict['buyer'] = list(part_dict['buyer'])
part_dict['supplier'] = list(part_dict['supplier'])
with open(f'TempJSONs/Parts/{part_name}.json', 'w') as file:
    json.dump(part_dict, file, ensure_ascii=False, indent=4)
print("Part file created")



# driver.quit()

