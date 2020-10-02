from bs4 import BeautifulSoup
import requests
import time, os
import re
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
chromedriver= '/Applications/chromedriver'
os.environ['webdriver.chrom.driver'] = chromedriver
site = 'https://get61.com/leaderboard'
page = requests.get(site).text
soup = BeautifulSoup(page, 'html5lib')

userlist = {'Ben Statz' : 'Casetta Bloody Mary', 'Ryan Kelly': 'RKD', 'Gena Rieger-Olson': 'The L is MSLGL',
           'Duncan Sweeney': 'Duncan', 'Jacob Hanke': 'jacobhanke12', 'Edward Mckenna': 'Dr Brad Peck', 'Thomas Gering': 'KingCrab',
           'Andrew Wells': '3SheepsToTheWind', 'Ticho': 'Andrew Ticho', 'Brett Falkowski': 'Falko',
           'Sam Reinertson': 'Riding Lawnmauer', 'Nate Bartz': 'Moonblatz', 'Bret Olson': 'Bert',
           'Dan Brunner': 'DPB', 'Srdjan Gajic': 'Provie'}
#print(soup.prettify())

driver = webdriver.Chrome(chromedriver)
driver.get(site)
soupy = BeautifulSoup(driver.page_source, 'html.parser')
playlise = re.compile('var names')
players = soup.find(text=playlise)
print(players)
