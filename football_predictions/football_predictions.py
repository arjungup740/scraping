import pandas as pd
import requests
import os
from bs4 import BeautifulSoup

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('precision', 1)

raw_html_pull = pd.read_html('https://www.pro-football-reference.com/boxscores/game-scores.htm')
raw_nfl = raw_html_pull[0]
working = raw_nfl.copy()

##### split out teams and dates
split_columns = working['Last Game'].str.split(',|vs.', expand = True)
working = working.join(split_columns).rename(columns = {0:'away', 1:'home', 2:'date', 3:'year'}) # away is always first, home second
working.groupby('year').count() # uh, how does the number of games vary each season.
working[working['year'] == 2010] # only 15 games from 2010, they are missing a lot of data this is BS
## working ['']
working[working['']]

raw_html_pull = pd.read_html('https://www.footballdb.com/games/index.html?lg=NFL&yr=2021')
response = requests.get('https://www.footballdb.com/games/index.html?lg=NFL&yr=2021')
print(response)

from selenium import webdriver
# DRIVER_PATH = '/path/to/chromedriver' # https://www.kenst.com/2015/03/including-the-chromedriver-location-in-macos-system-path/
DRIVER_PATH = f'{os.getcwd()}/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get('https://www.footballdb.com/games/index.html?lg=NFL&yr=2021')
# test = driver.find_element_by_class_name('statistics')
soup = BeautifulSoup(driver.page_source, 'html.parser')
list_of_tables = pd.read_html(driver.page_source)
season_scores = pd.concat(list_of_tables).rename(columns = {'Unnamed: 2':'visitor_score', 'Unnamed: 4':'home_score', 'Unnamed: 5':'was_OT'})
season_scores = season_scores[ ~((season_scores['visitor_score'] == 0) & (season_scores['home_score'] == 0)) ] # get rid of games that haven't happened yet
season_scores['home_team_won'] = season_scores['visitor_score'] > season_scores['home_score']
season_scores['home_team_won'] = season_scores['home_team_won'].replace({True:1, False:0})
season_scores.sum()
len(season_scores)
season_scores[ ~((season_scores['visitor_score'] == 0) & (season_scores['home_score'] == 0)) ]
