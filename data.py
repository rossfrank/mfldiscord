import config
import requests
import json
import api_requests
from fuzzywuzzy import process
from pathlib import Path
from datetime import datetime, timedelta

#creates player data if it doesn't exist
def create_if_not_exists(players=True):
    data_file = config.player_data if players else config.other_data
    data_file = Path(data_file)
    if not data_file.is_file():
            if players:
                prune_data(api_requests.get_players())
            else:
                save_data({'tradeBait': [],'pendingTrade': [], 'draftResults': []}, False)

#update trade file
def update_data(timestamps, type):
    create_if_not_exists()
    data = read_trade()
    data[type] = data[type] + timestamps
    write_bait_data(data)

#creates trade file if it doesn't exist
def create_if_not_exists():
    data_file = Path("trade.json")
    if not data_file.is_file():
        write_bait_data({'tradeBait': [],'pendingTrade': [], 'draftResults': []})

#get player data from file
def read_data(players=True):
    data_file = config.player_data if players else config.other_data
    create_if_not_exists(players)
    with open(data_file) as inputfile:
        return(json.load(inputfile))

#save player data to file
def save_data(data, players=True):
    data_file = config.player_data if players else config.other_data
    with open((data_file, 'w') as outfile:
        json.dump(data, outfile)

#removes bad_positions from data
def prune_data(data):
    y = []
    for x in data['player']:
        if x['position'] in config.positions:
            y.append(x)
    data['player'] = y
    save_data(data,True)
