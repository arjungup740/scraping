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

	# test = soup.extract('p').get_text().rstrip()
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

target_url = 'https://en.wikipedia.org/wiki/Brad_Pitt'
response = requests.get(
	url=target_url,
)
soup = BeautifulSoup(response.text, 'html.parser')

h1s = [x.get_text().rstrip() for x in soup.findAll('h1')]
h2s = [x.get_text().rstrip() for x in soup.findAll('h2')]
h3s = [x.get_text().rstrip() for x in soup.findAll('h3')]

h1s

### pull actor names in
list_of_1000_actors = pd.read_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors.csv')
## set up wikipedia links
list_of_1000_actors['wikipedia_url'] = 'https://en.wikipedia.org/wiki/' + list_of_1000_actors['name'].apply(lambda x: x.replace(' ', '_'))

## scrape baby
# start = datetime.datetime.now()
# list_of_1000_actors['wikipedia_url'].apply(scrape_wikipedia_page_of_text)
# end = datetime.datetime.now()
# print(end - start)

target_words_list = ['alcohol', 'alcoholism', 'rehab', 'drugs', 'drug abuse', 'addiction', 'addicted', 'sober since', 'drug offense', 'overdose', 'overdosing', 'cocaine', 'sober', 'drug use']
# actor_name = 'Ben_Affleck'
# pd.read_txt(f'{os.getcwd()}/actor_stuff/actor_bios/Aaron_Eckhart')
## check counts of words

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
df = pd.pivot_table(pd.melt(raw, id_vars = ['word'], var_name = 'actor', value_name = 'value'), index = 'actor', columns = 'word', values = 'value').reset_index()
df[df['actor'] == 'Angela_Lansbury']

scores = df.set_index('actor').sum(axis = 1)
scores[scores > 5] # doesn't pick up brad pitt, and it should


# todo AG:

# todo AG: can try training some sort of ML the way the name thing did

# can't do n-grams, just single words

### TODO
# grab all the h1, 2s, 3s, if any of them have a term then they definitely have had it
	# then figure out a way to also process it intelligently/incorporate it into the current analysis
# grab more words and terms to look for
# look into how the name people did ML on the names, apply it here
# look into putting up the 1st thousand pages on Mturk and seeing what happens