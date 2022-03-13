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

## sample
# target_url = 'https://en.wikipedia.org/wiki/Brad_Pitt'
# response = requests.get(
# 	url=target_url,
# )
# soup = BeautifulSoup(response.text, 'html.parser')


# h1s

### pull actor names in
list_of_1000_actors = pd.read_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors.csv')
## set up wikipedia links
list_of_1000_actors['wikipedia_url'] = 'https://en.wikipedia.org/wiki/' + list_of_1000_actors['name'].apply(lambda x: x.replace(' ', '_'))

# list_of_1000_actors.to_csv(f'{os.getcwd()}/actor_stuff/list_of_1000_actors_with_wiki_links.csv')

## scrape baby
# start = datetime.datetime.now()
# list_of_1000_actors['wikipedia_url'].apply(scrape_wikipedia_page_of_text)
# end = datetime.datetime.now()
# print(end - start)

target_words_list = ['married', 'marriage', 'divorce', 'divorced']
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

len(df[(df['divorce'] >= 1) | (df['divorced'] >= 1)]) # 487 out of 1000 actors have been divorced

#### try scraping the info box
target_url = 'https://en.wikipedia.org/wiki/Julie_Andrews'
response = requests.get(
	url=target_url,
)
soup = BeautifulSoup(response.text, 'html.parser')
test = soup.find('table', {"class" : "infobox biography vcard"})

elem_with_spouse_text = test(text = re.compile('Spouse'))
assert len(elem_with_spouse_text) == 1
elem_with_spouse_text[0].parent.parent.parent

num_times_married = len(soup(title = 'married'))
num_times_divorced = len(soup(title = 'divorced'))
num_times_separated = len(soup(title = 'separated'))
num_times_annulled = len(soup(title = 'annulled'))

soup(text = )



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
