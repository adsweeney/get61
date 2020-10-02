from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from datetime import datetime

# desired_width = 320
# pd.set_option('display.width', desired_width)
# pd.set_option("display.max_columns", 10)

sites = {'daily': 'https://get61.com/leaderboard', 'lifetime': 'https://get61.com/leaderboard?lifetime=true&sortBy=lifetime_score'}

userlist = {'Ben Statz' : 'Casetta Bloody Mary', 'Ryan Kelly': 'RKD', 'Gena Rieger-Olson': 'The L in MSLGL',
           'Duncan Sweeney': 'Duncan', 'Jacob Hanke': 'jacobhanke12', 'Edward Mckenna': 'Dr Brad Peck', 'Thomas Gering': 'KingCrab',
           'Andrew Wells': '3SheepsToTheWind', 'Ticho': 'Andrew Ticho', 'Brett Falkowski': 'Falko',
           'Sam Reinertson': 'Riding Lawnmauer', 'Nate Bartz': 'moonblatz', 'Bret Olson': 'Bert Olson',
           'Dan Brunner': 'DPB', 'Srdjan Gajic': 'Provie', 'James Madsen': 'James Madsen', 'Nate Woller': 'Woller',
           'Person1': 'The Merrill Advantage', 'Person2': 'Best Looking Guy in the WVC'}


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
                      columns=['names', 'score', 'hands', 'pickpct', 'winpct'])
    dflim = df[df.names.isin(userlist.values())]
    now = datetime.now()
    dflim['timestamp'] = now.strftime("%m/%d/%Y %H:%M:%S")
    dflim[['score', 'hands', 'pickpct', 'winpct']] = dflim[['score', 'hands', 'pickpct', 'winpct']].apply(pd.to_numeric)
    return dflim

print(get_leaderboard(sites['lifetime'], userlist))
