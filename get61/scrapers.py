from bs4 import BeautifulSoup
import requests
#import time, os
import re
#import urllib
#import json
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime

def get_leaderboard(site, userlist):
    page = requests.get(site).text
    soup = BeautifulSoup(page, 'html5lib')
    regser = re.compile('var names')
    datajav = soup.find(text=regser)
    
    cats = datajav.split('"')
    
    names = cats[1].split(',')
    score = cats[3].split(',')
    hands = cats[7].split(',')
    pickpct = cats[11].split(',')
    winpct = cats[13].split(',')
    
    df = pd.DataFrame(list(zip(names, score, hands, pickpct, winpct)),
                 columns = ['names', 'score', 'hands', 'pickpct', 'winpct'])
    dflim = df[df.names.isin(userlist.values())]
    now = datetime.now()
    dflim['timestamp'] = now.strftime("%m/%d/%Y %H:%M:%S")
    dflim[['score', 'hands', 'pickpct', 'winpct']] = dflim[['score', 'hands',      'pickpct', 'winpct']].apply(pd.to_numeric)
    return dflim


    



