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
        pendingTrades = tradeData.pending_trades()
        if pendingTrades:
            for x in pendingTrades:
                temp = discord.Embed(description=x)
                await client.send_message(channel, embed=temp)
        bait = tradeData.trade_bait()
        if bait:
            for x in bait:
                temp = discord.Embed(description=x)
                await client.send_message(channel, embed=temp)
        await asyncio.sleep(3600)

@client.event
async def on_message(message):
    if message.content.startswith('!points'):
        temp = discord.Embed(description='Calculating Points...')
        tmp = await client.send_message(message.channel, embed=temp)
        player = message.content.replace('!points ', '')
        player = playerData.find_player(player)
        score = api_requests.get_player_score(player['id'])['playerScore']['score']
        name = " ".join(player['name'].split(", ")[::-1])
        mes = name + ' averaged ' + score + 'pts'
        mes = discord.Embed(description=mes)
        await client.edit_message(tmp, embed=mes)
    elif message.content.startswith('!help'):
        help = discord.Embed(description="type !points {player name} to get player's average points per game")
        await client.send_message(message.channel, embed=help)
client.loop.create_task(hourly_background_task())
client.run(config.token)
