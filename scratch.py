import requests
import pandas as pd
import lxml
from bs4 import BeautifulSoup
import random
url = "https://en.wikipedia.org/wiki/List_of_Tom_Hanks_performances"
response = requests.get(
	url=url,
)
soup = BeautifulSoup(response.content, 'html.parser')

film_header = soup.find(id="Film")
soup.find_all('h2')

tables = soup.find_all('table')
tables.get_text(strip = True, separator= ' ')

test = pd.read_html(tables[0].prettify())

tables_list = [pd.read_html(x.prettify())[0] for x in tables]
headers = soup.find_all('h2')
headers[2].get_text(strip = True)
headers = soup.find_all('span', class = 'mw-headline')

tmp = soup.findAll('span',{'class':'mw-headline'})
table_names = [x.get_text('id') for x in tmp]

[pd.read_html(x.prettify())[0] for x in headers]


test2 = pd.read_html(url)
test3 = pd.read_html('https://en.wikipedia.org/wiki/Brad_Pitt_filmography')

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
b.join(a)