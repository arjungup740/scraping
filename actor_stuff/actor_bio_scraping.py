import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import datetime
from collections import Counter

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def scrape_wikipedia_page_of_text(target_url):
	response = requests.get(
		url=target_url,
	)
	soup = BeautifulSoup(response.text, 'html.parser')

	test = soup.extract('p').get_text().rstrip()
	test = soup.findAll('p')  # .get_text().rstrip()
	text_list = [x.get_text().rstrip() for x in test]
	full_text = ' '.join(text_list)

	actor_name = target_url.split('/')[-1]
	# open text file
	text_file = open(f'{os.getcwd()}/actor_stuff/actor_bios/{actor_name}', "w")
	# write string to file
	text_file.write(full_text)
	# close file
	text_file.close()

	return print(f'succesfully wrote {actor_name} file')


### pull actor names in
list_of_1000_actors = pd.read_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors.csv')
## set up wikipedia links
list_of_1000_actors['wikipedia_url'] = 'https://en.wikipedia.org/wiki/' + list_of_1000_actors['name'].apply(lambda x: x.replace(' ', '_'))

## scrape baby
# start = datetime.datetime.now()
# list_of_1000_actors['wikipedia_url'].apply(scrape_wikipedia_page_of_text)
# end = datetime.datetime.now()
# print(end - start)

target_words_list = ['alcohol', 'alcoholism', 'rehab', 'drugs', 'drug' 'abuse', 'addiction', 'addicted', 'sober since', 'drug offense', 'overdose', 'overdosing', 'cocaine', 'drug use']
actor_name = 'Aaron_Eckhart'
# pd.read_txt(f'{os.getcwd()}/actor_stuff/actor_bios/Aaron_Eckhart')


## check counts of words

big_dict = {}
for actor_name in sorted(os.listdir(f'{os.getcwd()}/actor_stuff/actor_bios/')):
	with open(f'{os.getcwd()}/actor_stuff/actor_bios/{actor_name}') as f:
		lines = f.readlines()
		key_words_dict = {}
		for word in target_words_list:
			key_words_dict[word] = Counter(lines[0].split(' '))[word]
		big_dict[actor_name] = key_words_dict

raw = pd.DataFrame(big_dict).reset_index().rename(columns = {'index':'word'})
raw.head()
df = pd.pivot_table(pd.melt(raw, id_vars = ['word'], var_name = 'actor', value_name = 'value'), index = 'actor', columns = 'word', values = 'value').reset_index()

df.sum()
df[df['actor'] == 'Brad_Pitt']
# todo AG: grab all the h1, 2s, 3s, if any of them have the term then they definitely have had it

# todo AG: can try training some sort of ML the way the name thing did