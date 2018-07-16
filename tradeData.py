import json
from pathlib import Path

import api_requests

#read trade file
def read_trade():
    create_if_not_exists()
    with open('trade.json') as inputfile:
        return(json.load(inputfile))

#update trade file
def update_trade(timestamps, type):
    create_if_not_exists()
    data = read_trade_bait()
    data[type] = data[type] + timestamps
    write_bait_data(data)

#creates trade file if it doesn't exist
def create_if_not_exists():
    data_file = Path("trade.json")
    if not data_file.is_file():
        write_bait_data({'tradeBait': [],'pendingTrade': []})

#write bait data
def write_bait_data(baitlist):
    with open('trade_bait.json', 'w') as outfile:
        json.dump(baitlist, outfile)

#pretty print draft pick
def draft_pick_info(pick):
    pick_info = pick.split('_')
    if pick_info[0] == 'DP':
        return('Round ' + str(int(pick_info[1]) + 1) + ' Pick ' + pick_info[2])
    else:
        franchise = get_franchise(1)
        import math
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
        output = franchise['name'] + ' ' + pick_info[2] + ' ' + ordinal(int(pick_info[3])) + ' Round Pick'
        return(output)

#get franchise info
def get_franchise(franchise_id):
    data = api_requests.get_league()
    for x in data['franchises']['franchise']:
        if x['id']:
            return(x)

#gets the trade bait to post and updates file
def check_if_post(trade, type):
    data = read_trade()[type]
    to_post = []
    if not isinstance(tradeBait, list):
        tradeBait = [tradeBait]
    for x in tradeBait:
        print(x)
        print(data)
        if x['timestamp'] not in data[type]:
            to_post.append(x)
    update_trade(list(map(lambda bait: bait['timestamp'],to_post)),type)
    return(to_post)

#pretty print bait info
def print_bait(bait):
    franchise = get_franchise(bait['franchise_id'])
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
    print(items)
    if len(items) == 1:
        str = items[0]
    else:
        for x in items:
            str = str + x + ' and '
        str = str[:-5]
    output = 'TRADE BAIT UPDATE: ' + franchise['name'] + ' will trade ' + str
    if bait['inExchangeFor']:
        output = output + ' for ' + bait['inExchangeFor']
    return(output)

def print_trade(trade):
    output = 'TRADE ALERT: ' + trade['description'] + ' VOTE TO APPROVE OR REJECT!!'
    return(output)

def trade_bait():
    data = api_requests.get_trade_bait()
    if data:
        to_post = check_if_post(data['tradeBait'],'tradeBait')
        return(map(lambda x: print_bait(x), to_post))

def pending_trades():
    data=api_requests.get_pending_trades()
    if data:
        to_post = check_if_post(data['pendingTrade'],'pendingTrade')
        return(map(lambda x: print_trade(x), to_post))
