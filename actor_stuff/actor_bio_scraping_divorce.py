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

def ping_for_data(target_url):
	response = requests.get(
		url=target_url,
	)
	soup = BeautifulSoup(response.text, 'html.parser')

	return soup

def scrape_wikipedia_page_of_text(target_url):
	"""
	Just pull the text of a target url and write it to a txt file
	:param target_url: the target url
	:return:
	"""
	## ping for data
	soup = ping_for_data(target_url)

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

def scrape_wikipedia_info_box_of_target(name, target_url):
	## TODO AG: This could probably be more modular -- intermediate step where you write the result somewhere and then just read from it going forward so not always pinging.
	## ping for data
	soup = ping_for_data(target_url)
	## parse results
	dict_of_results = {}
	dict_of_results['name'] = name
	abbrev_list = ['married', 'divorced', 'separated', 'annulled', 'cohabited']
	for marriage_result in abbrev_list:
		dict_of_results[marriage_result] = len(soup(title = marriage_result))

	return dict_of_results

#################################### Scrape wikipedia *text body* for 1000 actors
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
## easier, potentially wrong in edge cases and with smaller time actors, but very 80/20: Most have an abbreviation element with the title [married, divorced, separated, annulled]. Just grab those

# start = datetime.datetime.now()
# series_of_result_dicts = list_of_1000_actors.apply(lambda x: scrape_wikipedia_info_box_of_target(x.name_with_underscores, x.wikipedia_url), axis = 1) # https://stackoverflow.com/questions/13331698/how-to-apply-a-function-to-two-columns-of-pandas-dataframe
# info_box_df = pd.concat([pd.DataFrame(x, index = [0]) for x in series_of_result_dicts]).reset_index(drop = True)
# end = datetime.datetime.now()
# print(end - start) # 8 min for 1k, sequentially
## save down results
# info_box_df.to_csv(f'{os.getcwd()}/actor_stuff/divorce_df_from_info_box.csv')
info_box_df = pd.read_csv(f'{os.getcwd()}/actor_stuff/divorce_df_from_info_box.csv')

#################################### QA -- divorced/separated/annulled should generally == married, or married - 1
info_box_df['overall_marriage_fail_count'] = info_box_df['divorced'] + info_box_df['separated'] + info_box_df['annulled']
info_box_df['qa_col'] = ( (info_box_df['married'] == info_box_df['overall_marriage_fail_count']) | (info_box_df['married'] - 1 == info_box_df['overall_marriage_fail_count']) )
info_box_df[info_box_df['qa_col'] != True] # can't capture the "died" ones, since there's no abbreviation. for Lance Henriksen for example, there's no "div" abbrev

married_greater_than_1 = info_box_df[info_box_df['married'] > 1] # doesn't count people who get married once, then divorced once
overall_fails_greater_than_0 = info_box_df[info_box_df['overall_marriage_fail_count'] > 0]
never_married = info_box_df[info_box_df['married'] == 0]
set(overall_fails_greater_than_0['name']) - set(married_greater_than_1['name'])

len(never_married)
len(overall_fails_greater_than_0)
len(info_box_df[(info_box_df['married'] == 0) & (info_box_df['overall_marriage_fail_count'] > 0)]) # check never married, but divorced
len(info_box_df[(info_box_df['married'] > 0)])
len(info_box_df[(info_box_df['overall_marriage_fail_count'] > 0)])
len(info_box_df[(info_box_df['married'] > 1) | (info_box_df['overall_marriage_fail_count'] > 0)]) # broadest definition of failure
len(info_box_df[(info_box_df['married'] == 1) & (info_box_df['overall_marriage_fail_count'] == 0)]) # married once and that was it


#################################### pull in mturk
mturk = pd.read_csv(f'{os.getcwd()}/actor_stuff/divorce_mturk_results.csv', usecols = ['Input.document_url', 'Answer.category.label'])\
		  .rename(columns = {'Input.document_url':'url', 'Answer.category.label':'answer'})


response_tally = mturk.groupby('url')['answer'].apply(lambda x: Counter(x))\
			   		.reset_index()\
			        .rename(columns = {'level_1':'mturk_response', 'answer':'count_of_mturk_response'})
max_table = response_tally.groupby('url')['count_of_mturk_response'].max().reset_index()

selected_responses = response_tally.merge(max_table, on = ['url', 'count_of_mturk_response'])
selected_responses[selected_responses['count_of_mturk_response'] == 1]
## for now
selected_responses = selected_responses[selected_responses['count_of_mturk_response'] != 1]
selected_responses.groupby('mturk_response').count()

## merge in mturk answers to our scraped wikipedia answers
list_of_1000_actors
full_frame = info_box_df.merge(list_of_1000_actors[['name_with_underscores', 'wikipedia_url']], left_on = 'name', right_on = 'name_with_underscores', how = 'outer')\
		   .merge(selected_responses, left_on = ['wikipedia_url'], right_on = 'url', how = 'outer')\
		   .drop(['url', 'name_with_underscores', 'Unnamed: 0'], axis = 1)
## TODO AG: merge in wikipedia text method values values


list_of_1000_actors

# len(info_box_df[(info_box_df['married'] > 1) | (info_box_df['overall_marriage_fail_count'] > 0)])
len(full_frame[((full_frame['married'] > 1) | (full_frame['overall_marriage_fail_count'] > 0)) & (full_frame['mturk_response'] == 'Person has been married, got divorced')])
len(full_frame[((full_frame['married'] > 1) | (full_frame['overall_marriage_fail_count'] > 0)) & (full_frame['mturk_response'] != 'Person has been married, got divorced')])

## harder, potentially more accurate, much messier: pull the elements of the biography card and then work your way down to grab the info
# test = soup.find('table', {"class" : "infobox biography vcard"})
#
# elem_with_spouse_text = test(text = re.compile('Spouse'))
# assert len(elem_with_spouse_text) == 1
# elem_with_spouse_text[0].parent.parent.parent


### TODO
## pull in mturk answers and compare to other methods
	##


## nice to haves/technical improvements
	## clean up to have flags with if statements for each section (scrape, read from file, etc) rather than just comments everywhere
	## n-gram method
		## wrap it as a function for cleanliness
		## QA it, note problems/reliability for post
		## issues
			# not picking up the word "married" for Al Pacino
	## mturk method
		## come back and handle the 1,1,1s
	## refactor scraper for 1k function to store the html and then the values

