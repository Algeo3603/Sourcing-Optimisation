import os
from pathlib import Path
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar
from helium import *
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#------------------------------------------------------
#mechanize setup
cj = http.cookiejar.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("https://www.marklines.com/en/members/login")
#------------------------------------------------------


#---------------------------------------------------------
#mechanize login
br.select_form(nr=0)
br.form['profiles.login.login_id'] = 'N38wppXdYu'
br.form['profiles.login.password'] = 'pw776e'
br.submit()
#----------------------------------------------------------


#-------------------------------------------------------------------------------------
#User Input for part
inp=input("Enter Part Name: ")
br.follow_link(text="300 Components")
response=br.follow_link(text=inp)
#-------------------------------------------------------------------------------------


#-----------------------------------------------------------------
#getting parts data
soup = BeautifulSoup(response.get_data(), 'html.parser')
tbodies=soup.find_all('tbody')
tbody=tbodies[len(tbodies)-1]
td_tags = tbody.find_all('td')
data_list = [td.get_text().strip() for td in td_tags]
supplier_set=set()
#------------------------------------------------------------------



#REMOVE AFTER DATABASE INTEGRATION!!!!-----------------------------------------------------------
#Temporarily Removing commas from company names to store them in a comma delimited CSV File
i=0
while i<len(data_list):
   supplier_set.add(data_list[i+4])
   i=i+6
data_list = [element.replace(',', '') for element in data_list]
#REMOVE AFTER DATABASE INTEGRATION!!!!------------------------------------------------------------




#--------------------------------------------------------------------------------------------------
#Removing Model, Model Year from the data list, making tuples and 
#inserting them into a set to ensure there are no duplicates
tuple_set=set()
i=0
while i<len(data_list):
   tup=(data_list[i],data_list[i+1],data_list[i+4],data_list[i+5])
   tuple_set.add(tup)
   i=i+6
#--------------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------------
#Writing Parts data to a local file
with open('table.csv', 'w', encoding='utf-8') as file:
   i=0
   file.write("Region,Buyer,Supplier,Specific Part Name\n")
   for t in tuple_set:
      file.write(t[0]+','+t[1]+','+t[2]+','+t[3]+'\n')
#--------------------------------------------------------------------------------------------------



#---------------------------------------------------
#selenium setup
br.close()
exit()
url="https://www.marklines.com/en/members/login"
browser=start_chrome(url,headless=False)
#---------------------------------------------------



#---------------------------------------------------------------------------
#Selenium Login
username_field = browser.find_element(By.NAME,"profiles.login.login_id")  
password_field = browser.find_element(By.NAME,"profiles.login.password")
login_button=browser.find_element(By.ID,"login_btn")  

username_field.send_keys('HPKNtiUNat')
password_field.send_keys('pw684d')
login_button.click()
#-----------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------
#navigating to part information page
xpath_expression = "//a[contains(text(), '{}')]".format("300 Components")
link_element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
link_element.click()

xpath_expression = "//a[contains(text(), '{}')]".format(inp)
link_element = browser.find_element(By.XPATH, xpath_expression)
link_element.click()
#---------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------
#Following each supplier link, extracting data, writing to a local file
unresolved=set()
for element in supplier_set:
   data = {}
   print(element)
   
   
   #-------------------------------------------------------------------------------------------------
   #The supplier link is always not detected by selenium for some particular suppliers
   #Dont know the reason
   #These suppliers are added in the unresolved set
   try:
      link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, element)))
   except TimeoutException as e:
      unresolved.add(element)
      print("ABOVE ELEMENT IS UNRESOLVED")
      continue
   #--------------------------------------------------------------------------------------------------


   #---------------------------------------------------------------------------------      
   #following each link using javascript as following by link.click() is not reliable
   browser.execute_script("arguments[0].setAttribute('target', '_self');", link)
   browser.execute_script("arguments[0].scrollIntoView();", link)
   browser.execute_script("arguments[0].click();", link)
   soup=BeautifulSoup(browser.page_source,'html.parser')
   #----------------------------------------------------------------------------------



   #----------------------------------------------------------------------------------
   #top 500 suppliers and other suppliers have different data formats, 
   #require different methods to extract their data
   url=browser.current_url
   if 'top500' in url:
      soup=soup.find('div',class_='over-view')
      para=soup.find_all('p')
      info=[t.get_text().strip() for t in para]
      p=Path('suppliers')
      with open(p/f"{element}.txt",'w',encoding='utf-8') as file:
         file.write("TOP 500=TRUE\n")
         for i in range (0,len(info)):
            file.write(info[i])
            if i&1:
               file.write('\n')
            else:
               file.write(':')
         div=soup.find_all('div')
         d=div[len(div)-1]
         file.write(d.get_text().strip())
   else:
      soup=soup.find('div',id="basic-info")
      soup= soup.find('tbody')
      th=soup.find_all('th')
      th=[t.get_text().strip() for t in th]
      td=soup.find_all('td')
      td=[t.get_text().strip() for t in td]
      p=Path('suppliers')
      with open(p/f"{element}.txt",'w',encoding='utf-8') as file:
         file.write("TOP 500=FALSE\n")
         for i in range(0,len(td)):
            file.write(th[i]+':'+td[i]+'\n')
   #--------------------------------------------------------------------------------         
   browser.back()
browser.quit()
#---------------------------------------------------------------------------------------------------------------------
   