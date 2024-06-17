import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape():
    pass

part_name = input("Enter part name: ").strip().lower()
part_name = re.sub(' +', '-', part_name)
# part_name = 'brake-tube'
print(part_name)


link = 'https://www.zauba.com/import-' + part_name + '-hs-code.html'
# link = "https://www.google.com"
print(link)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
session = requests.Session()
response = session.get(link, headers=headers)
print("Status Code:", response.status_code)


try:
    html_data = response.text
    soup = BeautifulSoup(html_data, 'html.parser')
    
    # fetch all rows of the table
    table_rows = soup.find_all('tr')

    # get column headers for dataframe
    column_headers = [th.text for th in table_rows[0]]
    print(column_headers)

    # debug (single row)
    # r1 = [list(td.text for td in table_rows[1:])]
    # print(r1)
    
    all_rows = []
    for table_row in table_rows[1:]:
        values = [td.text for td in table_row]
        print(values)
        row_dict = {column_headers[i]: values[i] for i in range(len(column_headers))}
        print(row_dict)
        all_rows.append(row_dict)
    
except:
    print("Error!!!")
else:
    df = pd.DataFrame(all_rows, columns=column_headers)
    df.to_csv('imports_india.csv')