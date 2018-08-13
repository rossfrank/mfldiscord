import config
import discord
import asyncio
import requests
import json
import difflib
from fuzzywuzzy import process

import playerData
import api_requests
import franchiseData as data

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def update_players():
    playerData.check_age()

async def get_pending():
    pendingTrades = data.pending_trades()
    if pendingTrades:
        channel = client.get_channel(config.background_channel)
        for x in pendingTrades:
            temp = discord.Embed(description=x)
            await client.send_message(channel, embed=temp)

async def get_draft_results():
    results = data.get_draft_results()
    if results and len(results) > 1:
        channel = client.get_channel(config.draft_channel)
        for x in results:
            pick, ping = x
            temp = discord.Embed(description=pick)
            if ping:
                print(ping)
                user = channel.server.get_member_named(ping)
                pick = user.mention + " " + pick
            temp = discord.Embed(description=pick)
            await client.send_message(channel, embed=temp)

async def get_bait():
    bait = data.trade_bait()
    if bait:
        channel = client.get_channel(config.background_channel)
        for x in bait:
            temp = discord.Embed(description=x)
            await client.send_message(channel, embed=temp)

async def hourly_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(config.background_channel)
    while not client.is_closed:
        await update_players()
        await asyncio.sleep(3600)

async def quarter_hourly_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(config.background_channel)
    while not client.is_closed:
        await get_pending()
        await get_bait()
        await get_draft_results()
        await asyncio.sleep(300)

async def points(message):
    temp = discord.Embed(description='Calculating Points...')
    tmp = await client.send_message(message.channel, embed=temp)
    player = message.content.replace('!points ', '')
    player = playerData.find_player(player)
    score = api_requests.get_player_score(player['id'])['playerScore']['score']
    name = " ".join(player['name'].split(", ")[::-1])
    mes = name + ' averaged ' + score + 'pts'
    mes = discord.Embed(description=mes)
    await client.edit_message(tmp, embed=mes)

async def assets(message):
    temp = discord.Embed(description='Finding Assets...')
    tmp = await client.send_message(message.channel, embed=temp)
    assets = message.content.replace('!assets ', '')
    title, des = data.get_my_assets(assets)
    mes = discord.Embed(title=title, description=des)
    await client.edit_message(tmp, embed=mes)

async def abbrevs(message):
    temp = discord.Embed(description='Finding Abbreviations...')
    tmp = await client.send_message(message.channel, embed=temp)
    assets = message.content.replace('!assets ', '')
    title, des = data.get_abbrevs()
    mes = discord.Embed(title=title, description=des)
    await client.edit_message(tmp, embed=mes)

async def help_message(message):
    help_mes = "type !points {player name} to get player's average points per game"
    help_mes = help_mes + '\n' + 'type !abbrevs to get a list of all team abbreviations'
    help_mes = help_mes + '\n' + 'type !assets {Team Abbreviation} to get all draft picks for a team'
    helpMes = discord.Embed(description=help_mes)
    await client.send_message(message.channel, embed=helpMes)

@client.event
async def on_message(message):
    if message.content.startswith('!points'):
        await points(message)
    elif message.content.startswith('!assets'):
        await assets(message)
    elif message.content.startswith('!abbrevs'):
        await abbrevs(message)
    elif message.content.startswith('!help'):
        await help_message(message)

client.loop.create_task(hourly_background_task())
client.loop.create_task(quarter_hourly_background_task())
client.run(config.token)
