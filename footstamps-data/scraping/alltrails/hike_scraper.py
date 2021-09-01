import pymongo
import csv
import argparse
import requests
import os
import time
import re
import random
import logging
import calendar
import datetime
import pandas as pd

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Put your path to chrome driver here
# Download chromedriver if needed https://chromedriver.chromium.org/downloads
chrome_driver = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
os.environ["webdriver.chrome.driver"] = chrome_driver

# Set up logging and create file handler
FILE_LOGGING = 'scraping.log'
logger = logging.getLogger('scraping')
logger.setLevel(logging.INFO)

fh = logging.FileHandler(FILE_LOGGING, mode="w", encoding=None, delay=False)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

class HikeScraper:
    
    def __init__(self, trail_id, name, url, chrome_driver):
        super(HikeScraper, self).__init__()
        self.trail_id = trail_id
        self.name = name
        self.domain = 'https://www.alltrails.com'
        self.url = self.domain + url
        self.chrome_driver = chrome_driver
        self.ua = UserAgent().random
        self.soup = self.get_soup()
        self.trail_info = {}
        
        self.trail_info['name'] = name
        self.trail_info['_id'] = trail_id
        self.trail_info['url'] = self.url
        
    def time_now(self):
        '''Returns timestamp for current time for logging purposes'''
        time_now_str = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        return '***' + time_now_str + '*** '
    
    def get_soup(self):
        '''Returns soup of trail page after clicking show more button until no more reviews'''
        logger.info(self.time_now() + "Getting soup for " + self.name + ": " + self.url)
        try:
            options = Options() # Add fake useragent
            options.add_argument(f"user-agent={self.ua}") 
            driver = webdriver.Chrome(self.chrome_driver, options=options) # Connect driver and open page
            driver.get(self.url)

            n_clicks = 0
        
            while True:
                try:
                    show_more = driver.find_element_by_xpath("//button[@title='Show more reviews']")
                    show_more.click()
                    n_clicks += 1
                    if n_clicks > 350:
                        break
                except:
                    logger.info(self.time_now() + "No more reviews to show")
                    break    
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
        except:
            logger.info(self.time_now() + "Error skipping")
        return soup
        
    def scrape(self):
        '''Scrapes hike overview information'''
        try:
            soup = self.soup
        except:
            logger.info(self.time_now() + "Error skipping")

        # ---------- Hiking Overview ---------- #
        _div_overview = soup.find('div', {'class': 'styles-module__content___1GUwP'})
        ## Difficulty

        try:
            difficulty = _div_overview.select('span[class*="styles-module__diff___"]')[0].text
            self.trail_info['difficulty'] = difficulty
        except:
            logger.info(self.time_now() + "No difficulty present for this trail")
            
        ## Park
        try:
            _park_a = _div_overview.select('a')[0]
            park_name = _park_a.text
            park_url = self.domain + _park_a['href']
            self.trail_info['park'] = {}
            self.trail_info['park']['name'] = park_name
            self.trail_info['park']['url'] = park_url
        except:
            logger.info(self.time_now() + "No park information for this trail")
            
        ## Star Rating
        try:
            agg_rating_str = _div_overview.find('span', {'role': 'img'})['aria-label']
            m = re.search('[\d.]+', agg_rating_str)
            if m:
                self.trail_info['agg_rating'] = float(m[0])
        except:
            logger.info(self.time_now() + "No aggregate rating")
            
        # ---------- Location ---------- #
        self.trail_info['location'] = {}
        try:
            _g_maps = soup.select('a[href*="google.com/maps/dir"]')[0]['href']
            g_maps_url = _g_maps.replace('//', '')
            _pattern = r'(-?\d{1,}\.?\d{1,}),(-?\d{1,}\.?\d{1,})'
            m = re.search(_pattern, g_maps_url)
            if m:
                latitude = float(m[1])
                longitude = float(m[2])
                self.trail_info['location']['google_maps'] = g_maps_url
                self.trail_info['location']['latitude'] = latitude
                self.trail_info['location']['longitude'] = longitude
        except:
            logger.info(self.time_now() + "No geographical coordinates or maps")
            
        # State
        _pattern = '(?<=trail\/us\/)\w{1,}(?=\/)'
        m = re.search(_pattern, self.url)
        if m:
            self.trail_info['location']['state'] = m[0]
            
        # ---------- Description ---------- #
        try:
            _desc = soup.find('section', {'id': 'trail-top-overview-text'}).find('p').text
            self.trail_info['description'] = _desc
        except:
            logger.info(self.time_now() + "No trail description found")
            
        # ---------- Trail Stats ---------- #
        try:
            _stats = soup.find('section', {'id': 'trail-stats'}).select('span[class*="detail-data"]')
            if len(_stats) == 3:
                length_raw, elevation_gain_raw, route_type = (stat.text for stat in _stats)
                m1 = re.search('[\d.]+', length_raw)
                if m1:
                    self.trail_info['length_mi'] = float(m1[0])
                
                m2 = re.search('[\d,]+', elevation_gain_raw)
                if m2:
                    self.trail_info['elevation_gain_ft'] = float(m2[0].replace(',', ''))
                
                self.trail_info['route_type'] = route_type
        except:
            logger.info(self.time_now() + "No trail stats found")
            
        # ---------- Tag Cloud ---------- #
        try:
            _tags = soup.find('section', {'class': 'tag-cloud'}).select('span[class*="big rounded active"]')
            if _tags:
                tags = [tag.text for tag in _tags]
                self.trail_info['tags'] = tags
            else:
                logger.info(self.time_now() + "No tags found")
        except:
            logger.info(self.time_now() + "No tags found")
            
        # ---------- Reviews ---------- #
        try:
            _reviews = soup.find_all('div', {'itemprop': 'review'})
            if _reviews:
                reviews_list = [self.extract_review(review_div=rev, trail_id=self.trail_id, review_id=i) for i, rev in enumerate(_reviews)]
            self.trail_info['reviews'] = reviews_list
        except:
            logger.info(self.time_now() + "No reviews found")
            
    def extract_review(self, review_div, trail_id, review_id):
        '''Extract review information from review div class'''
        review = {}
        review['review_id'] = str(trail_id) + '-' + str(review_id)

        ## User Info
        name = review_div.find('div', {'class': 'styles-module__nameTrailDetails___3L6cM'}).text
        profile_url = self.domain + review_div.find('a', {'class': 'clickable styles-module__link48___1itag xlate-none styles-module__inlineBlock___2_3xn'})['href']
        username = re.search('(?<=\/members\/)[\w-]+', profile_url)[0]
        
        review['user'] = name
        review['username'] = username
        review['profile_url'] = profile_url

        ## Rating
        try:
            _div_details = review_div.find('div', {'class': 'styles-module__starsDateTrailDetails___3SBTN'})
            rating_str = _div_details.find('span', {'role': 'img'})['aria-label']
            m1 = re.search('[\d\.]+', rating_str)
            if m1:
                review['rating'] = float(m1[0])
        except:
            logger.info(self.time_now() + f"No rating for review_id {review_id}")
            
        ## Date
        calendar_map = {v: k for k,v in enumerate(calendar.month_name) if k != 0}
        try:
            date_str = _div_details.find('span', {'class': 'styles-module__dateTrailDetails___3qgZC xlate-none'}).text
            month_str, day, year = date_str.replace(',', '').split(' ')
            date_obj = datetime.datetime(int(year), calendar_map[month_str], int(day))
            review['date'] = date_obj
        except:
            logger.info(self.time_now() + f"No date for review_id {trail_id}-{review_id}")

        ## Tags
        try:
            _tags_div = review_div.find('div', {'class': 'styles-module__info___1Mbn6> styles-module__infoTrailDetails___23Xx3'})
            if _tags_div:
                tags = [tag.text for tag in _tags_div]
                review['tags'] = tags
        except:
            logger.info(self.time_now() + f"No tags for review_id {review_id}")

        ## Review Text
        try:
            _review_text = review_div.find('p', {'itemprop': 'reviewBody'}).text
            if _review_text:
                review['text'] = _review_text.strip()
        except:
            logger.info(self.time_now() + f"No review text for review_id {review_id}")
        
        return review

class DBAdapter:

    def __init__(self, user, password, host, db_name, collection_name):
        super(DBAdapter, self).__init__()
        self.client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}/{db_name}")[db_name][collection_name]
        
        logger.info(self.time_now() + "Connected to MongoDB")
    
    def check_exists(self, trail_id, url, name):
        '''Check to see if trail_id already exists in DB'''
        if self.client.count_documents({ '_id': trail_id }, limit = 1) != 0:
            logger.info(self.time_now() + f"Already exists skipped {trail_id}, {name}, {url}")
            return True
        else:
            return False
        
    def insert_one(self, trail_obj):
        '''Insert new document'''
        try:
            db.client.insert_one(trail_obj)
            logger.info(self.time_now() + f"Succesfully inserted {trail_obj['_id']}, {trail_obj['name']}, {trail_obj['url']}")
        except:
            logger.info(self.time_now() + f"Already exists skipped {trail_obj['_id']}, {trail_obj['name']}, {trail_obj['url']}")
        
    def find_all(self):
        '''Fetch all documents'''
        return [doc for doc in self.client.find()]
    
    def time_now(self):
        '''Returns timestamp for current time for logging purposes'''
        time_now_str = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        return '***' + time_now_str + '*** '

if __name__ == '__main__':
    logger.info('Script starts')

    def time_now():
        '''Returns timestamp for current time for logging purposes'''
        time_now_str = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        return '***' + time_now_str + '*** '

    # Read in Lu's scraped URLs and clean name/url
    FILE_TRAILS = './trails_20201003.csv'
    df_trails = pd.read_csv(FILE_TRAILS)
    df_trails = df_trails.loc[df_trails['url'].str.contains('/trail/us/'), ['name', 'url']] \
                .reset_index(drop=True) \
                .reset_index()
    df_trails.rename(columns={'index': 'trail_id'}, inplace=True)
    df_trails['name'] = df_trails['name'].str.replace('"', '').str.strip()
    df_trails['url'] = df_trails['url'].str.replace('"', '').str.strip()
    trails = df_trails.to_dict(orient='records') # Export as list of dicts

    # Initialize DB Adapter (bad practice to hardcode, sorry!)
    db = DBAdapter('user1', 'dva2020!', '35.227.61.30', 'outdoor', 'all_trails')

    num_trails = len(trails)
    random_order = random.sample(range(num_trails), num_trails)
    for i in random_order:
        trail_id, url, name = trails[i].values()
        # Check to see if trail_id already exists in
        if not db.check_exists(trail_id, url, name):
            hike = HikeScraper(trail_id, url, name, chrome_driver)
            #########################################################################################
            # THE BELOW WILL MODIFY THE MONGODB COLLECTION, DO NOT UNCOMMENT UNLESS NECESSARY
            #########################################################################################
            # try:
            #     hike.scrape()
            #     db.insert_one(hike.trail_info)
            # except:
            #     logger.info(time_now() + f' {trail_id}, {url}, {name}')