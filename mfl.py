import config
import discord
import asyncio
import requests
import json
import difflib
from fuzzywuzzy import process
client = discord.Client()

request_type = 'pendingTrades'

bad_positions = ['TMWR', 'TMRB', 'TMDL', 'TMLB', 'TMDB', 'TMTE', 'ST', 'Off', 'TMQB', 'TMPK', 'TMPN', 'Coach', 'PN']

api_request_pendingTrades = 'http://www' + config.server + '.myfantasyleague.com/' + config.year + '/export?TYPE=' + request_type  + '&L=' + config.league_id + '&APIKEY=' + config.api_key + '&FRANCHISE_ID=0000&JSON=1'

def api_request(request, params):
    return requests.get('http://www' + config.server + '.myfantasyleague.com/' + config.year + '/export?TYPE=' + request + '&L=' + config.league_id + '&APIKEY=' + config.api_key + '&'+ params +'&JSON=1').json()

with open('data.json') as inputfile:
    data = json.load(inputfile)

#y = []
#for x in data['players']['player']:
#    if x['position'] not in bad_positions:
#        y.append(x)

#data['players']['player'] = y

#with open('data-prune.json', 'w') as outfile:
#    json.dump(data, outfile)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def background_task():
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=discord_channel)
    while not client.is_closed:
        counter += 1
        #await client.send_message(channel, requests.get(api_request).json())
        await asyncio.sleep(60)


@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.startswith('!player'):
        player = message.content.replace('!player ', '')
        #await client.send_message(message.channel, api_request('playerStatus','P=' + findPlayer(player)['id']))
        await client.send_message(message.channel, findPlayer(player))

client.loop.create_task(background_task())
client.run(token)
