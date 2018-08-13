import config
import requests
import json
import api_requests
from fuzzywuzzy import process
from datetime import datetime, timedelta

import jsonData


#updates playerdb if older then 24 hrs
def check_age(data = ''):
    file_data = jsonData.read_data(config.players_file)
    if not data:
        data = file_data
    elif data['timestamp'] <= file_data['timestamp']:
            data = file_data
    now = datetime.now()
    if not now-timedelta(hours=24) <= datetime.fromtimestamp(float(data['timestamp'])) <= now:
        jsonData.write_data(input_file=config.players_file)

#get Player object from player's name
def get_player(name, data=read_data()):
    for x in data['player']:
        if x['name'] is name:
            return(x)

#gets player from id
def get_player_from_id(id, data=read_data(config.players_file)):
    for x in data['player']:
        if id == x['id']:
            return(x)

#gets a list of player names
def get_player_names(data=read_data(config.players_file)):
    players = []
    for x in data['player']:
        players.append(x['name'])
    return(players)

#searches the players and finds the closest match
def find_player(name):
    data = read_data(config.players_file)
    player_name , conf =  process.extractOne(name, get_player_names(data))
    return(get_player(player_name, data))
