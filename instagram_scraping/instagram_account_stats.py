import json
import pandas as pd
import requests
import os
from bs4 import BeautifulSoup

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('precision', 1)

from selenium import webdriver
# DRIVER_PATH = '/path/to/chromedriver' # https://www.kenst.com/2015/03/including-the-chromedriver-location-in-macos-system-path/
DRIVER_PATH = f'{os.getcwd()}/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get('https://www.instagram.com/tybuttrey/')
# driver.get('https://www.tiktok.com/')
driver.get('https://www.tiktok.com/@taylorswift?')
# https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver

# test = driver.find_element_by_class_name('statistics')
soup = BeautifulSoup(driver.page_source, 'html.parser')
with open(f'{os.getcwd()}/instagram_scraping/tikotk_tswift.txt', 'w') as f:
    f.write(soup.prettify())

json_version = json.loads(str(soup.text))

soup.prettify()#.to
test = soup.findAll('div')

# "authorStats":{"followerCount":8700000,"followingCount":0,"heart":86100000,"heartCount":86100000,"videoCount":22,"diggCount":394}
type(soup.find('authorStats'))

driver.page_source

test = soup.findAll('h2', {'class':'count_infos'})
soup
