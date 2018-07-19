import json
from pathlib import Path
from functools import reduce
import re

import api_requests

def string_reduce(l):
    return reduce((lambda x, y: x + '\n' + y), l)

#read trade file
def read_trade():
    create_if_not_exists()
    with open('trade.json') as inputfile:
        return(json.load(inputfile))

#update trade file
def update_trade(timestamps, type):
    create_if_not_exists()
    data = read_trade()
    data[type] = data[type] + timestamps
    write_bait_data(data)

#creates trade file if it doesn't exist
def create_if_not_exists():
    data_file = Path("trade.json")
    if not data_file.is_file():
        write_bait_data({'tradeBait': [],'pendingTrade': []})

#write bait data
def write_bait_data(baitlist):
    with open('trade.json', 'w') as outfile:
        json.dump(baitlist, outfile)

#pretty print draft pick
def draft_pick_info(pick):
    pick_info = pick.split('_')
    if pick_info[0] == 'DP':
        return('Round ' + str(int(pick_info[1]) + 1) + ' Pick ' + pick_info[2])
    else:
        franchise = get_individ_franchise(pick_info[1])
        import math
        ordinal = (lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4]))
        year = pick_info[2]
        r = ordinal(int(pick_info[3]))
        output = franchise['name'] + ' ' + year + ' ' + r + ' Round Pick'
        return(output)

#get franchise info
def get_individ_franchise(franchise_id):
    data = api_requests.get_league()
    for x in data['franchises']['franchise']:
        if x['id'] == franchise_id:
            return(x)

#gets the trade bait to post and updates file
def check_if_post(trade, call):
    data = read_trade()[call]
    to_post = []
    y = 'timestamp'
    if call == 'pendingTrade':
        y = 'expires'
    if not isinstance(trade, list):
        trade = [trade]
    for x in trade:
        if x[y] not in data:
            to_post.append(x)
    update_trade(list(map(lambda bait: bait[y],to_post)), call)
    return(to_post)

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

#pretty print bait info
def print_bait(bait):
    franchise = get_individ_franchise(bait['franchise_id'])
    offer = bait['willGiveUp'].split(',')
    items = []
    for x in offer:
        if '_' in x:
            items.append(draft_pick_info(x))
        else:
            import playerData
            name = playerData.get_player_from_id(x)['name']
            items.append(" ".join(name.split(", ")[::-1]))
    str = ''
    if len(items) == 1:
        str = items[0]
    else:
        for x in items:
            str = str + x + ' and '
        str = str[:-5]
    output = 'TRADE BAIT UPDATE: ' + franchise['name'] + ' will trade ' + str
    if bait['inExchangeFor']:
        output = output + ' for ' + cleanhtml(bait['inExchangeFor'])
    return(output)

def print_trade(trade):
    output = 'TRADE ALERT: ' + trade['description'] + ' VOTE TO APPROVE OR REJECT!!'
    return(output)

def trade_bait():
    data = api_requests.get_trade_bait()
    if data:
        to_post = check_if_post(data['tradeBait'],'tradeBait')
        return(list(map(lambda x: print_bait(x), to_post)))

def pending_trades():
    data=api_requests.get_pending_trades()
    if data:
        to_post = check_if_post(data['pendingTrade'],'pendingTrade')
        return(list(map(lambda x: print_trade(x), to_post)))

def get_franchise(abbrev):
    league = api_requests.get_league()['franchises']['franchise']
    for x in league:
        if 'abbrev' in x.keys() and abbrev == x['abbrev']:
            return(x)
    return('')

def get_assets(franchise):
    assets = api_requests.get_assets()
    for x in assets['franchise']:
        if x['id'] == franchise['id']:
            team = x
    curPicks = []
    for x in team['currentYearDraftPicks']['draftPick']:
        curPicks.append(x['description'])
    futPicks = []
    for x in team['futureYearDraftPicks']['draftPick']:
        futPicks.append(x['description'])
    return curPicks, futPicks

def get_abbrevs(title = ''):
    if not title:
        title = 'Abbreviations'
    franchises = api_requests.get_league()['franchises']['franchise']
    abbrevs = map((lambda x: "{:<6}".format(x['abbrev']) + '- ' + x['name']), franchises)
    return title, string_reduce(abbrevs)

def get_my_assets(abbrev):
    if not abbrev:
        #TODO get actual abbreviations
        return get_abbrevs(title = 'Wrong Abbreviation!')
    franchise = get_franchise(abbrev)
    if not franchise:
        curPicks, futPicks = get_assets(franchise)
        picks =  curPicks + futPicks
        sPicks = string_reduce(picks)
        title = "Assets for " + franchise['name']
        return title, sPicks
    else:
        return get_abbrevs(title = 'Wrong Abbreviation!')
