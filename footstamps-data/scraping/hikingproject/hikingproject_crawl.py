import requests
import re
from bs4 import BeautifulSoup

# Extract state id's from the directory webpage
r = requests.get('https://www.hikingproject.com/directory/areas')
soup = BeautifulSoup(r.text,'html.parser')
states ={}
for each in soup.find_all('div', class_='card'):
    link= each.find('a')['href']
    id_search = re.search('\d+',link)
    state_search = re.search('\w+-?\w+$',link)
    states[id_search.group()] = state_search.group()

# Extract all trails from each state
trail_ids = {}
for state_id in states.keys():
    print(states[state_id])
    idx = 0
    while True:
        link = f'https://www.hikingproject.com/ajax/area/{state_id}/trails?idx={idx}'
        r = requests.get(link)
        soup = BeautifulSoup(r.text, 'html.parser')
        trails = soup.find_all('tr')
        if trails:
            for trail in trails:
                link = trail['data-href']
                id_search = re.search('\d+',link)
                trail_ids[id_search.group(0)] = states[state_id]
            idx += 1
        else:
            break

with open('HPtrail_ids.csv', 'w') as f:
    for key in trail_ids.keys():
        f.write("%s,%s\n" % (key, trail_ids[key]))