import json
from pathlib import Path

import api_requests
import config

#read trade file
def read_trade(input_file):
    create_if_not_exists()
    with open(input_file) as inputfile:
        return(json.load(inputfile))

#update trade file
def update_data(timestamps='', type='', input_file):
    if input_file is config.data_file:
        create_if_not_exists(input_file)
        data = read_trade()
        data[type] = data[type] + timestamps
        write_data(data)
    elif input_file is config.players_file:
        create_if_not_exists(input_file)
        write_data(prune_data(api_requets.get_players()),input_file)

#creates trade file if it doesn't exist
def create_if_not_exists(input_file):
    data_file = Path(input_file)
    if not data_file.is_file() and input_file=config.data_file:
        write_data({'tradeBait': [],'pendingTrade': [], 'draftResults': []})
    elif not data_file.is_file() and input_file=config.players_file:
        write_data(prune_data(api_requests.get_players()))

#write bait data
def write_data(data, input_file):
    with open(input_file, 'w') as outfile:
        json.dump(data, outfile)

#removes bad_positions from data
def prune_data(data):
    y = []
    for x in data['player']:
        if x['position'] not in config.bad_positions:
            y.append(x)
    data['player'] = y
    return(data)
