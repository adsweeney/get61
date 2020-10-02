# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from bs4 import BeautifulSoup
import requests
# import time, os
import re
# import urllib
# import json
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
import numpy as np
import itertools

# %% [markdown]
# ## Setup

# %%
multipliers = dict(default = 1, no_schneider = 2, no_trick = 3, dob = 2, doubler = 2, blitz = 2, crack = 2, crack_back = 2, rb_crack = 4, base = 1, picker = 2)


# %%
hearts = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') + 'H' for i in range(7,15)]
clubs = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'D' for i in range(7,15)]
spades = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'S' for i in range(7,15)]
diamonds = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'D' for i in range(7,15)]


# %%
allcards = hearts + clubs + spades + diamonds
values = [0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11]


# %%
pointvalues = dict(zip(allcards, values))

# %% [markdown]
# ## Scrape

# %%
site = 'https://get61.com/hand_detail?handid=2268734'
page = requests.get(site).text
soup = BeautifulSoup(page, 'html5lib')


# %%
cardre = re.compile('var play11')
cards = soup.find(text=cardre)
raw_rows = cards.split(';')

b = raw_rows[0].split(' ')


# %%
hand_stats = [i.split(' ') for i in raw_rows]
hand_stats[1]


# %%
playnum = [hand_stats[i][1] for i in range(30)]
plays = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(30)]


# %%
leads = [int(hand_stats[i][3].replace('"', '')) for i in range(30, 36)]
scores = [int(hand_stats[i][3].replace('"', '')) for i in range(41, 46)]
bury = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(46,48)]
blind = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(48,50)]


# %%
# get names
nameslist = [row.split('=') for row in raw_rows[36:41]]
names = [nameslist[row][1].strip().replace('"', '') for row in range(5)]


# %%
namescol = []
for i in names:
    namescol.extend([i] * 6)


# %%
# playnum, plays, names, leads, scores, bury, blind
df = pd.DataFrame(playnum)
df.columns = ['playnum']
df['plays'] = plays
df['name'] = namescol


# %%
n = [1, 2, 3, 4, 5, 6]
trickloop = n* 5
#tricknums = [[str(i)] * 6 for i in range(1,7)]
#tricknums = list(itertools.chain.from_iterable(tricknums))
trickydic = dict(zip(playnum, trickloop))
df['trick'] = df['playnum'].map(trickydic)


# %%
positions = [1, 2, 3, 4, 5]
posdic = dict(zip(names, positions))
df['position'] = df['name'].map(posdic)


# %%
leadadj = [i + 1 for i in leads]

leadcond = [
    (df['trick'] == 1),
    (df['trick'] == 2),
    (df['trick'] == 3),
    (df['trick'] == 4),
    (df['trick'] == 5),
    (df['trick'] == 6)
]
values = [leadadj]
df['leader'] = np.select(leadcond, leadadj)


# %%
handpos1 = (df['name'] == names[0])
p = df[hands]
list(p['plays'])


# %%
handpos1 = list(df[df['name'] == names[0]]['plays'])
handpos2 = list(df[df['name'] == names[1]]['plays'])
handpos3 = list(df[df['name'] == names[2]]['plays'])
handpos4 = list(df[df['name'] == names[3]]['plays'])
handpos5 = list(df[df['name'] == names[4]]['plays'])


# %%
print(handpos1, names[0])
print(handpos2, names[1])
print(handpos3, names[2])
print(handpos4, names[3])
print(handpos5, names[4])


# %%
handposfive = df[df['name'] == names[4]]['plays']
handposfive


# %%
scores


# %%
ordereddf = df.sort_values(by=['trick', 'position'])
#df.sort_index()
#df.sort_values(by='playnum')
ordereddf


# %%



# %%
gr = ordereddf.groupby(['trick']).reset_index()


# %%
gr


# %%
allhands = [handpos1] + [handpos2] + [handpos3] + [handpos4] + [handpos5]

allhands


# %%
table = pd.DataFrame(allhands, columns =[1, 2, 3, 4, 5, 6])


# %%
table


# %%
table['points'] = scores


# %%
table


# %%



