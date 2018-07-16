import config
import requests
import json
import api_requests
from fuzzywuzzy import process
from pathlib import Path
from datetime import datetime, timedelta

bad_positions = ['TMWR', 'TMRB', 'TMDL', 'TMLB', 'TMDB', 'TMTE', 'ST', 'Off', 'TMQB', 'TMPK', 'TMPN', 'Coach', 'PN']

#creates player data if it doesn't exist
def create_if_not_exists():
    data_file = Path("player_data.json")
    if not data_file.is_file():
        save_data(prune_data(api_requests.get_players()))

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
        if x['position'] not in bad_positions:
            y.append(x)
    data['player'] = y
    save_data(data)

#updates playerdb if older then 24 hrs
def check_age(data = ''):
    create_if_not_exists()
    file_data = read_data()
    if not data:
        data = file_data
    elif data['timestamp'] <= file_data['timestamp']:
            data = file_data
    now = datetime.now()
    if not now-timedelta(hours=24) <= datetime.fromtimestamp(float(1531529144)) <= now:
        prune_data(api_requests.get_players())

#get Player object from player's name
def get_player(name, data=read_data()):
    for x in data['player']:
        if x['name'] is name:
            return(x)

#gets player from id
def get_player_from_id(id, data=read_data()):
    for x in data['player']:
        if id == x['name']:
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
