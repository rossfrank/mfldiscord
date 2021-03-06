import config
import requests
import json
import api_requests
import tradeData
from fuzzywuzzy import process
from pathlib import Path
from datetime import datetime, timedelta

#creates player data if it doesn't exist
def create_if_not_exists():
    data_file = Path("player_data.json")
    if not data_file.is_file():
        prune_data(api_requests.get_players())

#get player data from file
def read_data():
    create_if_not_exists()
    with open('player_data.json') as inputfile:
        return(json.load(inputfile))

#save player data to file
def save_data(data):
    with open('player_data.json', 'w') as outfile:
        json.dump(data, outfile)

#removes bad_positions from data
def prune_data(data):
    y = []
    for x in data['player']:
        if x['position'] in config.positions:
            y.append(x)
    data['player'] = y
    save_data(data)

#updates playerdb if older then 24 hrs
def check_age(data = ''):
    file_data = read_data()
    if not data:
        data = file_data
    elif data['timestamp'] <= file_data['timestamp']:
            data = file_data
    now = datetime.now()
    if not now-timedelta(hours=24) <= datetime.fromtimestamp(float(data['timestamp'])) <= now:
        prune_data(api_requests.get_players())

#get Player object from player's name
def get_player(name, data=read_data()):
    for x in data['player']:
        if x['name'] is name:
            return(x)

#gets player from id
def get_player_from_id(id, data=read_data()):
    for x in data['player']:
        if id == x['id']:
            return(x)

#gets a list of player names
def get_player_names(data=read_data()):
    players = []
    for x in data['player']:
        players.append(x['name'])
    return(players)

#searches the players and finds the closest match
def find_player(name):
    data = read_data()
    player_name , conf =  process.extractOne(name, get_player_names(data))
    return(get_player(player_name, data))

def print_status(name):
    player_status, player = get_player_status(name)
    player_name = " ".join(player['name'].split(", ")[::-1])
    return(player_name + ' is on ' + player_status['status'])

def get_player_status(name):
    player = find_player(name)
    return((api_requests.get_player_status(player['id']),player))

#gets roster
def get_roster(abbrev):
    franchise = tradeData.get_franchise(abbrev)
    if not franchise:
        return tradeData.get_abbrevs(title = 'Wrong Abbreviation!')
    roster = api_requests.get_roster(franchise['id'])['franchise']
    return(roster['player'])

def print_players(players, ir_taxi=True):
    result = []
    for player,status in players:
        name = " ".join(player['name'].split(", ")[::-1])
        s = ''
        if status == 'TAXI_SQUAD':
            s = ', TAXI'
        elif status == 'INJURED_RESERVE':
            s = ', IR'
        if ir_taxi or status == 'ROSTER':
            result.append(name + ' ' + player['position'] + ', ' + player['team'] + s)
    return('\n'.join(result))

def print_players_ir_taxi(players):
    result = []
    for player in players:
        name = " ".join(player['name'].split(", ")[::-1])
        result.append(name + ' ' + player['position'] + ', ' + player['team'])
    return('\n'.join(result))

def rookie_check(player):
    try:
        if player['status'] == 'R':
            return True
    except:
        return False
    return False

def print_players_rookie(roster):
    results = []
    for position in config.positions:
        try:
            rookies = filter(lambda x: rookie_check(x[0]),roster[position])
            if rookies:
                results.append(position + ':')
                for player,status in rookies:
                    temp = " ".join(player['name'].split(", ")[::-1])
                    if not status == 'ROSTER':
                        s = 'IR'
                        if status.split('_')[0] == 'TAXI':
                            s = 'TAXI'
                        temp = temp + ', ' + 'TAXI'
                    results.append(temp)
        except:
            continue
    return('\n'.join(results))


def get_by_position(abbrev, position = ''):
    if not abbrev:
        return tradeData.get_abbrevs(title = 'Wrong Abbreviation!')
    players = get_roster(abbrev)
    taxi = []
    roster = {}
    ir = []
    data = read_data()
    for p in players:
        player = get_player_from_id(p['id'], data)
        if player['position'] in roster.keys():
            roster[player['position']].append((player,p['status']))
        else:
            roster[player['position']] = [(player,p['status'])]
        if p['status'] == 'TAXI_SQUAD':
            taxi.append(player)
        elif p['status'] == 'INJURED_RESERVE':
            ir.append(player)
    if position == 'TAXI':
        return(('Taxi Squad',print_players_ir_taxi(taxi)))
    elif position == 'IR':
        return(('IR',print_players_ir_taxi(ir)))
    elif position == 'R':
        return(('Rookies',print_players_rookie(roster)))
    elif position in roster.keys():
        return((position,print_players(roster[position])))
    result = []
    for pos in config.positions:
        try:
            result.append(print_players(roster[pos], False))
        except:
            continue
    print_taxi = print_players_ir_taxi(taxi)
    if print_taxi:
        result.append('TAXI')
        result.append(print_taxi)
    print_ir = print_players_ir_taxi(ir)
    if print_ir:
        result.append('IR')
        result.append(print_ir)
    #result = result + 'TAXI:\n' + print_players_ir_taxi(taxi) + '\nIR:\n' + print_players_ir_taxi(ir)
    return(('Roster','\n'.join(result)))
