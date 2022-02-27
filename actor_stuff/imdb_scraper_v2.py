import os
import requests
import pandas as pd
# import lxml
from bs4 import BeautifulSoup
import datetime

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# pd.set_option('precision', 1)


def pull_actor_lists(list_url):

	imdb_list_response = requests.get(list_url)

	soup = BeautifulSoup(imdb_list_response.content, 'html.parser')
	tmp = soup.findAll('h3', {'class':'lister-item-header'})

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

	return df_of_rankings

def get_filmography_soup_obj(url):

	actor_page = requests.get(url)
	soup = BeautifulSoup(actor_page.content, 'html.parser')
	filmography = soup.find(class_='filmo-category-section')

	return filmography


def get_filmo_df(filmo_class, filmography):
	list_of_dfs = []
	for index in range(len(filmography.find_all(class_ = filmo_class))):
		# actor vs. director
		role_type = filmography.find_all(class_ = filmo_class)[index].get('id') # actor, prodcuer, director, etc
		# year movie came out
		year = filmography.find_all(class_ = filmo_class)[index].find(class_ = 'year_column').get_text(strip = True)
		# movie name
		movie_name = filmography.find_all(class_ = filmo_class)[index].find('a').get_text()

		tmp_df = pd.DataFrame({'role_type':role_type, 'year':year, 'movie_name':movie_name}, index = [0])
		list_of_dfs.append(tmp_df)
	film_df = pd.concat(list_of_dfs)

	return film_df

def get_odd_and_even_films(filmography):
	odd_films = get_filmo_df('filmo-row odd', filmography)
	even_films = get_filmo_df('filmo-row even', filmography)
	all_films = pd.concat([odd_films, even_films])

	return all_films

list_of_ranking_dfs = []
for i in range(1, 11):
	list_url = f'https://www.imdb.com/list/ls058011111/?sort=list_order,asc&mode=detail&page={i}'
	df_of_rankings = pull_actor_lists(list_url)
	list_of_ranking_dfs.append(df_of_rankings)

df_of_rankings = pd.concat(list_of_ranking_dfs)
# df_of_rankings.to_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors.csv')

dict_of_dfs = {}
start = datetime.datetime.now()
for url in df_of_rankings['imdb_full_link'].tolist(): # [0:2]
	filmography = get_filmography_soup_obj(url)
	actor_df = get_odd_and_even_films(filmography)
	dict_of_dfs[url] = actor_df
end = datetime.datetime.now()
print(end - start)

actors_and_movies = pd.concat(dict_of_dfs).reset_index().drop('level_1', axis = 1).rename(columns = {'level_0':'imdb_full_link'})
actors_and_movies.to_csv(f'{os.getcwd()}/actors_and_movies_to_262.csv')

actors_and_movies = pd.read_csv(f'{os.getcwd()}/actors_and_movies_to_262.csv')
merged = actors_and_movies.merge(df_of_rankings, on = 'imdb_full_link').drop('Unnamed: 0', axis = 1)
# merged['year'] = pd.to_numeric(merged['year'])
merged['year'] = merged['year'].str.replace('/I?(II)?(III)?(IV)?', '', regex = True)
merged['year'] = merged['year'].str.replace('[A-Z]', '', regex = True)
# merged[merged['year'].str.contains('[A-Z]', na = False)]
merged[['year', 'year_2']] = merged['year'].str.split(	'-', n = 2, expand = True)
merged['year'] = pd.to_numeric(merged['year'])
merged['year_2'] = pd.to_numeric(merged['year_2'])
merged['rank'] = pd.to_numeric(merged['rank'])
merged.groupby('name')['movie_name'].count().describe()
## want movies/year, so get max(year), min(year), subtract 2 and # films /
merged.groupby('name').agg({'year':'max', 'year':'min'})

from rotten_tomatoes_scraper.rt_scraper import MovieScraper
def rotten_tomatoes_review_puller(movie_title):
	print(f'pulling data for {movie_title}')
	try:
		movie_scraper = MovieScraper(movie_title = movie_title)
		movie_scraper.extract_metadata()
		metadata_dict = movie_scraper.metadata

		return metadata_dict
	except Exception as e:
		print(f'failed on {movie_title}')

	# metadata_dict['Score_Rotten']
	# metadata_dict['Score_Audience']

start = datetime.datetime.now()
merged['rotten_tomatoes_metadata'] = merged['movie_name'].apply(rotten_tomatoes_review_puller)
end = datetime.datetime.now()
print(end - start)

########### parallelize getting rotten tomatoes data
from dask.distributed import Client
# client = Client() # blows everything up
from dask import delayed
results = delayed(rotten_tomatoes_review_puller)(merged['movie_name'])
results.visualize()
test = results.compute()
list_of_delayeds = [delayed(rotten_tomatoes_review_puller)(x) for x in merged['movie_name']]


####### scrape movie grosses
# https://www.boxofficemojo.com/chart/top_lifetime_gross/?area=XWW
# https://www.imdb.com/search/title/?title_type=feature&sort=boxoffice_gross_us,desc&ref_=adv_prv
# https://www.kaggle.com/c/tmdb-box-office-prediction/data
list_of_movie_grosses = []
for i in range(1, 9999, 50):
	print(f'starting page {i}')
	url = f'https://www.imdb.com/search/title/?title_type=feature&sort=boxoffice_gross_us,desc&start={i}&view=advanced'
	grosses_response = requests.get(url)
	grosses_soup = BeautifulSoup(grosses_response.content, 'html.parser')
	all_movie_blocks_on_page = grosses_soup.find_all('div', {'class':'lister-item mode-advanced'})
	for movie_index in range(50):
		movie_name = all_movie_blocks_on_page[movie_index].find('div', {'class':'lister-item-content'}).find('h3').find('a').get_text()
		year = all_movie_blocks_on_page[movie_index].find('div', {'class':'lister-item-content'}).find('h3').find(class_ = "lister-item-year text-muted unbold").get_text()
		gross = all_movie_blocks_on_page[movie_index].find('div', {'class':'lister-item-content'}).find(class_ = "sort-num_votes-visible").findAll('span')[-1]['data-value']
		list_of_movie_grosses.append((movie_name, year, gross))
		print(f'finished {movie_name}')

import pickle as pkl
filename = 'list_of_grosses'
outfile = open(filename,'wb')
pkl.dump(list_of_movie_grosses,outfile)
outfile.close()

test = pd.read_html('https://www.dentaldepartures.com/dentist/dental-clinic-sulejmanagic')