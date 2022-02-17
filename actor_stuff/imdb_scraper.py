import requests
import pandas as pd
import lxml
from bs4 import BeautifulSoup
import random
imdb_list_response = requests.get('https://www.imdb.com/list/ls058011111/')
imdb_list_response.content

soup = BeautifulSoup(imdb_list_response.content, 'html.parser')
tmp = soup.findAll('a')
tmp = soup.findAll('h3', {'class':'lister-item-header'})
tmp[0].get('href')

[x.get_text(strip = True) for x in tmp[0].findChildren()]
[x.get('href') for x in tmp[0].findChildren()]

link_list = []
data_list = []
for index in range(len(tmp)):
	link_list.append([x.get('href') for x in tmp[index].findChildren()])
	data_list.append([x.get_text(strip = True) for x in tmp[index].findChildren()])

index = 0
pd.DataFrame([x.get('href') for x in tmp[index].findChildren()])
a = pd.DataFrame(link_list, columns = ['redundant', 'imdb_stub_link'])
b = pd.DataFrame(data_list, columns = ['rank', 'name'])
df_of_rankings = b.join(a).drop('redundant', axis = 1)
df_of_rankings['imdb_full_link'] = 'https://www.imdb.com' + df_of_rankings['imdb_stub_link']
df_of_rankings

url = 'https://www.imdb.com/name/nm0000134'
# url = 'https://www.imdb.com/name/nm0000197'
url = 'https://www.imdb.com/name/nm0914612'
actor_page = requests.get(url)
actor_page.content
soup = BeautifulSoup(actor_page.content, 'html.parser')
filmography = soup.find(id = 'filmography')
filmography = soup.find(class_ = 'filmo-category-section')

# actor vs. director
filmography.find_all(class_ = 'filmo-row odd')[0].get('id')#.findChildren()#.find()#[3]#.get_text()
# year movie came out
filmography.find_all(class_ = 'filmo-row odd')[0].find(class_ = 'year_column').get_text(strip = True)
# movie name
filmography.find_all(class_ = 'filmo-row odd')[4].find('a').get_text()


filmo_class = 'filmo-row odd'
def get_film_df(filmo_class):
	list_of_dfs = []
	for index in range(len(filmography.find_all(class_ = filmo_class))):
		role_type = filmography.find_all(class_ = filmo_class)[index].get('id') # actor, prodcuer, director, etc
		year = filmography.find_all(class_ = filmo_class)[index].find(class_ = 'year_column').get_text(strip = True)
		movie_name = filmography.find_all(class_ = filmo_class)[index].find('a').get_text()
		tmp_df = pd.DataFrame({'role_type':role_type, 'year':year, 'movie_name':movie_name}, index = [0])
		list_of_dfs.append(tmp_df)
	film_df = pd.concat(list_of_dfs)

	return film_df

odd_films = get_film_df('filmo-row odd')
even_films = get_film_df('filmo-row even')
all_films = pd.concat([odd_films, even_films])

filmography.find(id = 'actor-tt0179492')

# all text
filmography.find_all(class_ = 'filmo-row odd')[4].get_text()#('a')#[0]

test = filmography.find_all(class_ = 'filmo-row odd')[4].findChildren()

filmography.find_all(class_ = 'filmo-row odd')[0].find('b').get_text() # todo why can't extract the <a href = ...>, need xpath?
filmography.find_all(class_ = 'filmo-row odd')[0].find('a').get_text()

filmography.findChildren()[0].find('a')

filmography.findChildren()[0].get('href')
filmography[0].find(class_ = 'filmo_category_section').get_text()

test = requests.get('https://en.wikipedia.org/wiki/Mel_Gibson#Personal_life')

# for i in filmography:
# 	print(i.div)