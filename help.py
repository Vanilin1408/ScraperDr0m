# Test some options
from bs4 import BeautifulSoup
import requests

# Testing for take a count of ads
response = requests.get('https://simferopol.drom.ru/lada/granta/?distance=1000')
response_soup = BeautifulSoup(response.text, 'lxml')

# Take a tag info about count and convert to "int"
str_info_count_ads: str = response_soup.find('div', class_='css-1xkq48l eckkbc90').text.split(' ')[0]
amount_ads: str = ''.join([char for char in str_info_count_ads if char.isdigit()])
print(str_info_count_ads, amount_ads)
