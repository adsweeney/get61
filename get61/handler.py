from scrapers import get_leaderboard
import pandas as pd
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np

hearts = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') + 'H' for i in range(7,15)]
clubs = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'D' for i in range(7,15)]
spades = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'S' for i in range(7,15)]
diamonds = [str(i).replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A')  + 'D' for i in range(7,15)]

allcards = hearts + clubs + spades + diamonds
values = [0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11]

pointvalues = dict(zip(allcards, values))

#%%
def get_hands(handnum):
    site = 'https://get61.com/hand_detail?handid={}'
    page = requests.get(site.format(handnum)).text
    soup = BeautifulSoup(page, 'html5lib')

    cardreg = re.compile('var play11')
    elements = soup.find(text=cardreg)
    raw_rows = elements.split(';')

    hand_stats = [i.split(' ') for i in raw_rows]

    playnum = [hand_stats[i][1] for i in range(30)]
    plays = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(30)]

    leads = [int(hand_stats[i][3].replace('"', '')) for i in range(30, 36)]
    scores = [int(hand_stats[i][3].replace('"', '')) for i in range(41, 46)]
    bury = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(46,48)]
    blind = [hand_stats[i][3].replace('"', '').replace('11', 'J').replace('12', 'Q').replace('13', 'K').replace('14', 'A') for i in range(48,50)]

    nameslist = [row.split('=') for row in raw_rows[36:41]]
    names = [nameslist[row][1].strip().replace('"', '') for row in range(5)]

    namescol = []
    for i in names:
        namescol.extend([i] * 6)

    df = pd.DataFrame(playnum)
    df.columns = ['playnum']
    df['plays'] = plays
    df['name'] = namescol

    n = [1, 2, 3, 4, 5, 6]
    trickloop = n* 5
    trickydic = dict(zip(playnum, trickloop))
    df['trick'] = df['playnum'].map(trickydic)

    positions = [1, 2, 3, 4, 5]
    posdic = dict(zip(names, positions))
    df['position'] = df['name'].map(posdic)

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

    ordereddf = df.sort_values(by=['trick', 'position']).reset_index()

    handpos1 = list(df[df['name'] == names[0]]['plays'])
    handpos2 = list(df[df['name'] == names[1]]['plays'])
    handpos3 = list(df[df['name'] == names[2]]['plays'])
    handpos4 = list(df[df['name'] == names[3]]['plays'])
    handpos5 = list(df[df['name'] == names[4]]['plays'])
    
    return ordereddf, handpos1, handpos2, handpos3, handpos4, handpos5



df, h1, h2, h3, h4, h5 = get_hands('2268734')
print(h1, h2, h3 ,h4, h5)
# %%
