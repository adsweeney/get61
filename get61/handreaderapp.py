import cv2
import numpy as np
import pandas as pd
import os
from itertools import combinations, permutations
import joblib
import time

cardimages = os.listdir('get61imgs')

heartsa = [str(i) + 'H' for i in range(7,15)]
clubsa = [str(i) + 'C' for i in range(7,15)]
spadesa = [str(i) + 'S' for i in range(7,15)]
diamondsa = [str(i) + 'D' for i in range(7,15)]

allcardsa = heartsa + clubsa + spadesa + diamondsa
valuesa = [0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11, 0, 0, 0, 10, 2, 3, 4, 11]

pointvalues = dict(zip(allcardsa, valuesa))

log_reg = joblib.load('log_reg_mod.joblib')

# card types
hearts = [str(i) + 'H' for i in range(7, 11)] + ['13H'] + ['14H']
spades = [str(i) + 'S' for i in range(7, 11)] + ['13S'] + ['14S']
clubs = [str(i) + 'C' for i in range(7, 11)] + ['13C'] + ['14C']
# Trump
trump = [str(i) + 'D' for i in range(7, 15)] + ['11' + i for i in ['H', 'S', 'C']] + ['12' + i for i in ['H', 'S', 'C']]
fail = hearts + spades + clubs
points = [0, 0, 0, 10, 4, 11]
pointstrump = [0, 0, 0, 10, 2, 3, 4, 11, 2, 2, 2, 3, 3, 3]
trumprank = [1, 2, 3, 5, 7, 11, 4, 6, 8, 9, 10, 12, 13, 14]
failrank = [1, 2, 3, 5, 4, 6]

faildic = dict(zip(fail, zip(points * 4, failrank * 4)))
trumpdic = dict(zip(trump, zip(pointstrump, trumprank)))

start_hand = ['12C', '12D', '11S', '10D', '8H', '9S']


def get_cards(preblind):
    cards_in_hand = []
    for i in cardimages:
        #img_rgb = cv2.imread('goodpickhandblindsmall.png')
        img_rgb = cv2.imread(preblind)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread('get61imgsorig/{}'.format(i),0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.95


        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        
        #cv2.imwrite('res{}.png'.format(i),img_rgb)
        if any(map(len, loc)):
            cards_in_hand.append(i)
            #cv2.imwrite('found_cards/res{}.png'.format(i),img_rgb)
    return cards_in_hand

preblind = input('start? ')
time.sleep(3)
preblind = ['12C', '12D', '11S', '10D', '8H', '9S']    
#cards_in_hand = get_cards(preblind)
cards_in_hand = preblind
cards= [i.replace('.png','') for i in cards_in_hand]
trumphand = sorted([i for i in cards if i in trumpdic.keys()], key=lambda x: trumpdic[x][1], reverse=True)
failhand = sorted([i for i in cards if i in faildic.keys()], key=lambda x: faildic[x][1], reverse=True)
points_in_hand = sum([pointvalues[i] for i in cards])
trumpcount = len(trumphand)
failcount = len(failhand)
possible_hands = list(combinations(cards, 6))
held_points = points_in_hand
#print('\n',cards)



position = int(input('Please Enter your Table Position (1-5): '))
time.sleep(1)
pick_position = 2
print('\nTrump: ', trumphand)
print('\nFail: ', failhand)

preblind.append(pick_position)
preblind.append(trumpcount)
preblind.append(held_points)
inp_columns = [1, 2, 3, 4, 5, 6, 'pick_position', 'trumpcount', 'heldpoints']
data = preblind
checkdf = pd.DataFrame(columns=inp_columns)
a_series = pd.Series(data, index=checkdf.columns)
checkdf = checkdf.append(a_series, ignore_index=True)
compdf = pd.read_pickle('new_hands_df')
compdf = compdf.iloc[:, 2:-1]
checkdfdum = pd.get_dummies(checkdf, columns = [1, 2, 3, 4, 5, 6])
missing_cols = set(compdf.columns) - set(checkdfdum.columns)
for c in missing_cols:
    checkdfdum[c] = 0
checkdfdum = checkdfdum[compdf.columns]
checkX = checkdfdum.iloc[:,:]

predscheck = log_reg.predict(checkX)
probacheck = log_reg.predict_proba(checkX)

print('\nShould you pick this hand?')
print('\nOutcome: ', predscheck[0])
print('Probability of winning: ', probacheck[0][1])
print('\n')

postblind = input('Picked up?: ')
time.sleep(3)
postblind = ['12C', '12D', '11S', '10D', '8H', '9S', '7D', '12H']

#cards_in_hand = get_cards(postblind)
cards_in_hand = postblind
cards= [i.replace('.png','') for i in cards_in_hand]
trump_hand = sorted([i for i in cards if i in trumpdic.keys()], key=lambda x: trumpdic[x][1], reverse=True)
fail_hand = sorted([i for i in cards if i in faildic.keys()], key=lambda x: faildic[x][1], reverse=True)
points_in_hand = sum([pointvalues[i] for i in cards])
trumpcount = len(trump)
failcount = len(fail)
possible_hands = list(combinations(cards, 6))
held_points = points_in_hand
print('\n',postblind)
print('\nRunning Model on all 28 possible hands')
time.sleep(1)
inp_columns = [1, 2, 3, 4, 5, 6, 'pick_position', 'trumpcount', 'heldpoints']
data = []
for i in possible_hands:
    d = list(i)
    d.append(pick_position)
    data.append(d)
ts = []
for i in data:
    t = [j for j in i if j in trumpdic.keys()]
    tc = len(t)
    i.append(tc)
for i in data:
    p = sum([pointvalues[j] for j in i[:6]])
    i.append(p)
    
#print(data)

checkdf = pd.DataFrame(data, columns=inp_columns)

#print(checkdf)

compdf = pd.read_pickle('new_hands_df')
compdf = compdf.iloc[:, 2:-1]
checkdfdum = pd.get_dummies(checkdf, columns = [1, 2, 3, 4, 5, 6])
missing_cols = set(compdf.columns) - set(checkdfdum.columns)
for c in missing_cols:
    checkdfdum[c] = 0
checkdfdum = checkdfdum[compdf.columns]
checkX = checkdfdum.iloc[:,:]

#predscheck = log_reg.predict(checkX)
probacheck = log_reg.predict_proba(checkX)
prob = np.amax(probacheck, axis=0)[1]
hand_to_play_index = np.where(probacheck == np.amax(probacheck, axis=0)[1])

best_hand = data[hand_to_play_index[0][0]][:6]
# print('Best Hand')
# print('Outcome: Win')
# print('probability: ', prob)
best_hand = sorted(best_hand, key=lambda x: trumpdic[x][1], reverse=True)
p_bury = p_bury = list(combinations(cards, 2))
mylis = []
for i, j in p_bury:
    if any(x in [i, j] for x in trump):
        continue
    else:
        mylis.append([i, j])

maxi = 0
two = ''
for pair in mylis:
    total = sum([pointvalues[i] for i in pair])
    if total > maxi:
        maxi = total
        two = pair

print('\nTrump: ', trump_hand, ' ', len(trump_hand))
print('\nFail: ', fail_hand, ' ', len(fail_hand))
print('\nBest Hand Available: ', best_hand)
print('Probabilty of Winning: ', prob)
bbbbury = np.setdiff1d(postblind, best_hand)
#print('\nMax Bury:', two, maxi)
print('Bury: ', bbbbury)
print('\n')

recc = input('Bury Recomended Cards? (yes/no)')
#bury1 = input('What did you bury first? ')
#print(bury1)
#bury2 = input('What did you bury second? ')
#print(bury2)
my_bury = ['8H', '9S']
#print(my_bury)
my_pile = my_bury
print('\nBuried: ', my_pile)
print('\n')

print('------------------------------------')
trick1 = input('\nfirst trick played')
time.sleep(3)
taken = input('Did you take this trick? (y / n) ')


trick1 = ['10C', '14C', '8C', '11S', '9C']
trick2 = ['12C', '13D', '8D', '12S', '9D']
trick3 = ['12D', '14D', '11D', '13S', '11H']
trick4 = ['12H', '7H', '13C', '9H', '11C']
trick5 = ['10D', '7S', '10S', '7C', '13H']
trick6 = ['7D', '8S', '10H', '14H', '14S']

#print(trick1)
trick1points = sum([pointvalues[i] for i in trick1])
print('\nlast trick', trick1, '>>', trick1points, ' pts')
#print('\n{} points in this trick'.format(trick1points))
my_pile.extend(trick1)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)

trump_rem = sorted([x for x in trump if x not in trick1 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = sorted([x for x in hearts if x not in trick1 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs if x not in trick1 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades if x not in trick1 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in trick1
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')
print('------------------------------------')
trick2 = input('\nSecond trick played')
time.sleep(2)
taken = input('Did you take this trick? (y / n) ')
trick2 = ['12C', '13D', '8D', '12S', '9D']

trick2points = sum([pointvalues[i] for i in trick2])
print('\nlast trick', trick2, '>>', trick2points, ' pts')
#print('\n{} points in this trick'.format(trick2points))
my_pile.extend(trick2)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)

trump_rem = sorted([x for x in trump_rem if x not in trick2 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = sorted([x for x in hearts_rem if x not in trick2 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs_rem if x not in trick2 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades_rem if x not in trick2 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in trick2
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')
print('------------------------------------')
trick3 = input('\nThird trick played')
time.sleep(3)
taken = input('Did you take this trick? (y / n) ')
trick3 = ['12D', '14D', '11D', '13S', '11H']

trick3points = sum([pointvalues[i] for i in trick3])
print('\nlast trick', trick3, '>>', trick3points, ' pts')
#print('\n{} points in this trick'.format(trick3points))
my_pile.extend(trick3)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)


trump_rem = sorted([x for x in trump_rem if x not in trick3 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = sorted([x for x in hearts_rem if x not in trick3 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs_rem if x not in trick3 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades_rem if x not in trick3 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in my_pile
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')

print('------------------------------------')
trick4 = input('\nFourth trick played')
time.sleep(3)
taken = input('Did you take this trick? (y / n) ')
trick4 = ['12H', '7H', '13C', '9H', '11C']

trick4points = sum([pointvalues[i] for i in trick4])
print('\nlast trick', trick4, '>>', trick4points, ' pts')
#print('\n{} points in this trick'.format(trick4points))
my_pile.extend(trick4)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)


trump_rem = sorted([x for x in trump_rem if x not in trick4 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = sorted([x for x in hearts_rem if x not in trick4 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs_rem if x not in trick4 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades_rem if x not in trick4 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in my_pile
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')

print('------------------------------------')
trick5 = input('\nFifth trick played')
time.sleep(3)
taken = input('Did you take this trick? (y / n) ')
trick5 = ['7D', '8S', '10H', '14H', '14S']

trick5points = sum([pointvalues[i] for i in trick5])
print('\nlast trick', trick5, '>>', trick5points, ' pts')
#print('\n{} points in this trick'.format(trick5points))
my_pile.extend(trick5)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)


trump_rem = sorted([x for x in trump_rem if x not in trick5 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = [x for x in hearts_rem if x not in trick5 + cards + my_bury]#, key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs_rem if x not in trick5 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades_rem if x not in trick5 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in my_pile
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')
print('------------------------------------')
trick6 = input('\nSixth trick played')
time.sleep(3)
taken = input('Did you take this trick? (y / n) ')
trick6 = ['10D', '7S', '10S', '7C', '13H']

trick6points = sum([pointvalues[i] for i in trick6])
print('\nlast trick', trick6, '>>', trick6points, ' pts')
#print('\n{} points in this trick'.format(trick6points))
my_pile.extend(trick6)
#print('\nMy Card Pile: ' , my_pile)
mypoints = sum([pointvalues[i] for i in my_pile])
print('\nMy Points: ', mypoints)


trump_rem = sorted([x for x in trump_rem if x not in trick6 + cards], key=lambda x: trumpdic[x][1], reverse=True)
hearts_rem = sorted([x for x in hearts_rem if x not in trick6 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
clubs_rem = sorted([x for x in clubs_rem if x not in trick6 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
spades_rem = sorted([x for x in spades_rem if x not in trick6 + cards + my_bury], key=lambda x: faildic[x][1], reverse=True)
jackd = '11D' in my_pile
print('\nTrump Remaining:  ', len(trump_rem), ' ', trump_rem)
print('\nHearts Remaining: ', len(hearts_rem), ' ', hearts_rem)
print('\nClubs Remaining:  ', len(clubs_rem), ' ', clubs_rem)
print('\nSpades Remaining: ', len(spades_rem), ' ', spades_rem)
print('\nHas Partner (JD) been Revealed? ', jackd)
print('\n')

