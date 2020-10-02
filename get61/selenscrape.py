from bs4 import BeautifulSoup
import requests
import time, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chromedriver= '/Applications/chromedriver'
os.environ['webdriver.chrom.driver'] = chromedriver

site = 'https://get61.com/leaderboard?lifetime=true&sortBy=daily_score'
driver = webdriver.Chrome(chromedriver)
driver.get(site)
time.sleep(10)
zpath = '//*[@id="{}"]/td[{}]'
rawtable = []
for i in range(50):
    row2 = []
    for j in range(1,8):
        row2.append(driver.find_element_by_xpath(zpath.format(i,j)).text)
    rawtable.append(row2)
df = pd.DataFrame.from_records(rawtable)

print(df.head(10))
