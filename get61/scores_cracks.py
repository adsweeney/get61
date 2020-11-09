"""[summary]

Returns:
    [type]: [description]
"""
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
#import time, os
# import urllib
#import json
import pandas as pd



sites = {'daily': 'https://get61.com/leaderboard',
         'lifetime': 'https://get61.com/leaderboard?lifetime=true&sortBy=lifetime_score',
         'player_pages': 'https://get61.com/player_profile?player={}'}

userlist = {'Ben Statz' : 'Casetta Bloody Mary', 'Ryan Kelly': 'RKD', 'Gena Rieger-Olson':
            'The L in MSLGL', 'Duncan Sweeney': 'Duncan', 'Jacob Hanke': 'jacobhanke12',
            'Edward Mckenna': 'Dr Brad Peck', 'Thomas Gering': 'KingCrab',
            'Andrew Wells': '3SheepsToTheWind', 'Ticho': 'Andrew Ticho', 'Brett Falkowski': 'Falko',
            'Sam Reinertson': 'Riding Lawnmauer', 'Nate Bartz': 'moonblatz',
            'Bret Olson': 'Bert Olson',
            'Dan Brunner': 'DPB', 'Srdjan Gajic': 'Provie', 'James Madsen': 'James Madsen',
            'Nate Woller': 'Woller',
            'Person1': 'The Merrill Advantage', 'Person2': 'Best Looking Guy in the WVC',
            'Denman': 'Denman', 'j':'jbeam1', 'byd':'bigyellowdog'
            }


def get_leaderboard(site, users):
    """Returns Lifetime Leaderboard

    Args:
        site (string): website
        userlist (dictionary): names and usernames

    Returns:
        dataframe: leaderboard table
    """
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
    authcodes = cats[5].split(',')
    d_f = pd.DataFrame(list(zip(names, score, hands, pickpct, winpct, authcodes)),
                       columns=['usernames', 'score', 'hands', 'pickpct', 'winpct', 'authcodes'])
    dflim = d_f[d_f.usernames.isin(users.values())]
    now = datetime.now()
    dflim['timestamp'] = now.strftime("%m/%d/%Y %H:%M:%S")
    dflim[['score', 'hands', 'pickpct', 'winpct']] = dflim[['score', 'hands', 'pickpct', 'winpct'
                                                            ]].apply(pd.to_numeric)

    authdic = dict(zip(dflim['usernames'], dflim['authcodes']))
    return dflim, authdic


def crack_score(playercodes):
    """Lifetime crack scores

    Args:
        playercodes (dictionary): usernames with google / facebook auth identifiers

    Returns:
        dataframe: table of crack scores
    """
    users = []
    cracks = []
    won_cracks = []
    for player in playercodes.values():

        response = requests.get(sites['player_pages'].format(player)).text
        soup = BeautifulSoup(response, 'html5lib')

        regser = re.compile('var numCracks')
        rawsource = soup.find(text=regser)
        rawlisted = rawsource.split(';')
        rawstripped = [row.strip("'\nvar") for row in rawlisted]
        stats = [line.split('=') for line in rawstripped]
        users.append(stats[1][1].replace('"', ''))
        cracks.append(stats[2][1].replace('"', ''))
        won_cracks.append(stats[28][1].replace('"', ''))

    crack_df = pd.DataFrame(list(zip(users, cracks, won_cracks)),
                            columns=['names', 'cracks_lifetime', 'cracks_won'])
    crack_df[['cracks_lifetime', 'cracks_won']] = crack_df[['cracks_lifetime',
                                                            'cracks_won']].apply(pd.to_numeric)
    crack_df['winpct_cracks'] = crack_df['cracks_won'] / crack_df['cracks_lifetime']
    return crack_df

score_df, playercode = get_leaderboard(sites['lifetime'], userlist)
crack_dff = crack_score(playercode)

print(score_df.drop(['authcodes'], axis=1))
print(crack_dff.sort_values(['winpct_cracks'], ascending=True))
