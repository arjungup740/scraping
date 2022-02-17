import requests
from bs4 import BeautifulSoup

response = requests.get(
	url="https://en.wikipedia.org/wiki/Matthew_Perry",
)
soup = BeautifulSoup(response.content, 'html.parser')

soup.extract('p').get_text()