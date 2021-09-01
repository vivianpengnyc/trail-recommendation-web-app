#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import sys
import numpy as np
import pandas as pd
import regex as re
import csv


# In[2]:


from webdriver_manager.chrome import ChromeDriverManager

chrome_driver = webdriver.Chrome(ChromeDriverManager().install())


# In[3]:


chrome_driver = '/Users/vivianpeng/.wdm/drivers/chromedriver/mac64/85.0.4183.87/chromedriver'
os.environ["webdriver.chrome.driver"] = chrome_driver


# In[126]:


trail_id = []
with open('./HPtrail_ids.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for i in reader:
        trail_id.append(i[0])


# In[123]:


class HPScraper:
    def __init__(self, chrome_driver):
        self.chrome_driver = chrome_driver
        #Add fake useragent
        options = Options()
        options.add_argument(f"user-agent={UserAgent().random}")
        
        #Connect driver andopen page in test mdode
        self.driver = webdriver.Chrome(self.chrome_driver, options=options)

        

    def get_comments(self, trail: str):
        comment_list = []
        link = 'https://www.hikingproject.com/trail/' + trail

        #Connect driver andopen page in test mdode
        self.driver.get(link)

        #Scroll to the bottom of the page
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Get soup of final page and find all trails
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        comments = soup.find_all('div', class_="comment-body")

        for info in comments:
            comment_list.append(info.find('span').text)
        
        # get overview
        try:
            overview = soup.find('h2', class_="text-xs-center").text
        except AttributeError:
            overview = ''
        
        # get Dogs, Features
        try:
            top_features = soup.find_all('span', class_="font-body pl-half")
            dogs = top_features[0].text
            features = top_features[1].text
        except AttributeError:
            dogs = ''
            features = ''
        except IndexError:
            dogs = ''
            features = ''
        # get other text information
            
                   
        alltext_li = []

        try: 
            alltext = soup.find('div', id = "trail-text").find_all('div', class_="mb-1")
            alltext_li = []
            for item in alltext[2:5]:
                alltext_li.append(item.text)
        except AttributeError:
            all_text = []
        except IndexError:
            all_text = []
            
        return comment_list, overview, dogs, features, alltext_li
    
        
    
    def close_driver(self):
        self.driver.quit()


# In[132]:


df_master= pd.DataFrame(columns = ['trail_id', 'overview', 'comments', 'Dogs', 'Features', 'Description'])

trail_scraper = HPScraper(chrome_driver)

no = 0

for ID in trail_id:
    li, overview, dogs, features, description = trail_scraper.get_comments(ID)
    new_row = {'trail_id': ID, 'overview': overview, 'comments': li, "Dogs": dogs, "Features": features, "Description": description}
    df_master = df_master.append(new_row, ignore_index = True)
    print(no)
    print(ID + ' this trail is completed')
    no = no + 1
    
trail_scraper.driver.quit()
df_master.to_csv('comments.csv')
