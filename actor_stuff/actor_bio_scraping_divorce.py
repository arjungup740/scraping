import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import datetime
import re
from collections import Counter

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def scrape_wikipedia_page_of_text(target_url):
	"""
	Just pull the text of a target url and write it to a txt file
	:param target_url: the target url
	:return:
	"""
	response = requests.get(
		url=target_url,
	)
	soup = BeautifulSoup(response.text, 'html.parser')

	# test = soup.extract('p').get_text().rstrip()
	test = soup.findAll('p')  # .get_text().rstrip()
	text_list = [x.get_text().rstrip() for x in test]
	full_text = ' '.join(text_list)

	## get the headers, if one of them mentions a target word then high likelihood
	h1s = [x.get_text().rstrip() for x in soup.findAll('h1')]
	h2s = [x.get_text().rstrip() for x in soup.findAll('h2')]
	h3s = [x.get_text().rstrip() for x in soup.findAll('h3')]

	actor_name = target_url.split('/')[-1]
	# open text file
	text_file = open(f'{os.getcwd()}/actor_stuff/actor_bios/{actor_name}', "w")
	# write string to file
	text_file.write(full_text)
	# close file
	text_file.close()

	return print(f'succesfully wrote {actor_name} file')

#################################### Scrape wikipedia *text* for 1000 actors
### pull actor names in
list_of_1000_actors = pd.read_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors.csv')
## set up wikipedia links
list_of_1000_actors['name_with_underscores'] = list_of_1000_actors['name'].apply(lambda x: x.replace(' ', '_')) # separate field for convenience later on
list_of_1000_actors['wikipedia_url'] = 'https://en.wikipedia.org/wiki/' + list_of_1000_actors['name_with_underscores']
## write with the wikipedia links to a file to upload to mturk
# list_of_1000_actors.to_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors_with_wiki_links.csv')
### scrape the bios and write to a folder so later can just pull from there
# start = datetime.datetime.now()
# list_of_1000_actors['wikipedia_url'].apply(scrape_wikipedia_page_of_text)
# end = datetime.datetime.now()
# print(end - start)

#################################### Get counts of target words from bios
target_words_list = ['married', 'marriage', 'divorce', 'divorced']

big_dict = {}
for actor_name in sorted(os.listdir(f'{os.getcwd()}/actor_stuff/actor_bios/')):
	with open(f'{os.getcwd()}/actor_stuff/actor_bios/{actor_name}') as f:
		lines = f.read()
		key_words_dict = {}
		for word in target_words_list:
			key_words_dict[word] = Counter(lines.split(' '))[word]
		big_dict[actor_name] = key_words_dict

raw = pd.DataFrame(big_dict).reset_index().rename(columns = {'index':'word'})
raw.head()
bio_df = pd.pivot_table(pd.melt(raw, id_vars = ['word'], var_name = 'actor', value_name = 'value'), index = 'actor', columns = 'word', values = 'value').reset_index()

len(bio_df[(bio_df['divorce'] >= 1) | (bio_df['divorced'] >= 1)]) # 487 out of 1000 actors have been divorced

#################################### Scrape the info box
## easier, potentially wrong in edge cases, but very 80/20: Most have an abbreviation element with the title [married, divorced, separated, annulled]. Just grab those

def ping_for_data(target_url):
	response = requests.get(
		url=target_url,
	)
	soup = BeautifulSoup(response.text, 'html.parser')

	return soup

def scrape_wikipedia_info_box_of_target(name, target_url):
	## TODO AG: This could probably be more modular -- intermediate step where you write the result somewhere and then just read from it going forward so not always pinging.
	## ping for data
	soup = ping_for_data(target_url)
	## parse results
	dict_of_results = {}
	dict_of_results['name'] = name
	abbrev_list = ['married', 'divorced', 'separated', 'annulled']
	for marriage_result in abbrev_list:
		dict_of_results[marriage_result] = len(soup(title = marriage_result))

	return dict_of_results

# https://stackoverflow.com/questions/13331698/how-to-apply-a-function-to-two-columns-of-pandas-dataframe
series_of_result_dicts = list_of_1000_actors.iloc[0:4].apply(lambda x: scrape_wikipedia_info_box_of_target(x.name_with_underscores, x.wikipedia_url), axis = 1)
info_box_df = pd.concat([pd.DataFrame(x, index = [0]) for x in series_of_result_dicts]).reset_index(drop = True)

## harder, potentially more accurate, much messier: pull the elements of the biography card and then work your way down to grab the info
# test = soup.find('table', {"class" : "infobox biography vcard"})
#
# elem_with_spouse_text = test(text = re.compile('Spouse'))
# assert len(elem_with_spouse_text) == 1
# elem_with_spouse_text[0].parent.parent.parent


### TODO
##### think simply on what needs to happen next
	## try the n-gram method to classify people as divorced or not
		## wrap it as a function for cleanliness
		## QA it, note problems/reliability for post
		## issues
			# not picking up the word "married" for Al Pacino
	## set up an mturk task
	## scrape the info boxes of people
		## wrap it as a function
		## scrape for 1k, store the html and then the values
