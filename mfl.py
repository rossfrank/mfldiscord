import config
import discord
import asyncio
import requests
import json
import difflib
from fuzzywuzzy import process

import playerData
import api_requests
import tradeData


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def hourly_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(config.background_channel)
    while not client.is_closed:
        playerData.check_age()
        for x in tradeData.pending_trades():
            await client.send_message(channel, x)
        for x in tradeData.trade_bait():
            await client.send_message(channel, x)
        await asyncio.sleep(3600)


async def background_task():
    await client.wait_until_ready()
    channel = client.get_channel(config.background_channel)
    while not client.is_closed:
        await client.send_message(channel, "test10")
        await asyncio.sleep(10)

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!points'):
        tmp = await client.send_message(message.channel, 'Calculating Points...')
        player = message.content.replace('!points ', '')
        player = playerData.find_player(player)
        score = api_requests.get_player_score(player['id'])['playerScore']['score']
        name = " ".join(player['name'].split(", ")[::-1])
        mes = name + ' averaged ' + score + 'pts'
        await client.edit_message(tmp, mes)

client.loop.create_task(hourly_background_task())
client.run(config.token)
