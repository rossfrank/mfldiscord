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

async def update_players():
    playerData.check_age()

async def get_pending():
    try:
        pendingTrades = tradeData.pending_trades()
        if pendingTrades:
            channel = client.get_channel(config.background_channel)
            for x in pendingTrades:
                temp = discord.Embed(description=x)
                await client.send_message(channel, embed=temp)
    except:
        pass

async def dez(message):
    temp = discord.Embed(description='Finding Team...')
    print(message)
    tmp = await client.send_message(message.channel, embed=temp)
    team = playerData.get_player_from_id('9823')['team']
    name = 'Dez Bryant'
    if 'FA' in team:
        result = name + ' is still a Free Agent'
    else:
        result = name + ' HAS BEEN SIGNED BY ' + team
    mes = discord.Embed(description=result)
    await client.edit_message(tmp, embed=mes)

async def get_draft_results():
    results = tradeData.get_draft_results()
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
    bait = tradeData.trade_bait()
    if bait:
        channel = client.get_channel(config.background_channel)
        for x in bait:
            temp = discord.Embed(description=x)
            await client.send_message(channel, embed=temp)

async def quarter_hourly_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(config.background_channel)
    while not client.is_closed:
        await get_pending()
        await get_bait()
        if config.draft:
            await get_draft_results()
        await update_players()
        await asyncio.sleep(300)

async def points(message):
    temp = discord.Embed(description='Calculating Points...')
    tmp = await client.send_message(message.channel, embed=temp)
    items = message.content.split(' ')
    #player = message.content.replace('!points ', '')
    try:
        if len(items) is 4 and items[3].isdigit():
            week = items[3]
        else:
            week = 'AVG'
        player = playerData.find_player(items[1] + ' ' + items[2])
        scores = api_requests.get_player_score(player['id'],week)['playerScore']
        if week is 'AVG':
            score = scores['score']
            verb = ' averaged '
            tail = ''
        else:
            for s in scores:
                if s['week'] is week:
                    score = s['score']
                    break
            verb = ' scored '
            tail = ' in week ' + week
        if not score:
            score = '0'
        name = " ".join(player['name'].split(", ")[::-1])
        mes = name + verb + score + ' pts' + tail
        if name == 'Dez Bryant':
            mes = 'Dez Bryant is not on a team, therefore he scores no points'
    except:
        mes = 'Your command is wrong'
    mes = discord.Embed(description=mes)
    await client.edit_message(tmp, embed=mes)

async def assets(message):
    temp = discord.Embed(description='Finding Assets...')
    tmp = await client.send_message(message.channel, embed=temp)
    assets = message.content.replace('!assets ', '')
    try:
        title, des = tradeData.get_my_assets(assets.upper())
    except:
        title = 'Bad Assets'
        des = 'Your command is wrong'
    mes = discord.Embed(title=title, description=des)
    await client.edit_message(tmp, embed=mes)

async def abbrevs(message):
    temp = discord.Embed(description='Finding Abbreviations...')
    tmp = await client.send_message(message.channel, embed=temp)
    title, des = tradeData.get_abbrevs()
    mes = discord.Embed(title=title, description=des)
    await client.edit_message(tmp, embed=mes)

async def roster(message):
    temp = discord.Embed(description='Finding Roster...')
    tmp = await client.send_message(message.channel, embed=temp)
    try:
        input = message.content.replace('!roster ', '')
        input = input.split(' ')
        position = ''
        if len(input) is 2:
            position = input[1]
        title, des = playerData.get_by_position(input[0].upper(),position.upper())
    except:
        title = 'Error'
        des = 'Your Command is wrong'
    mes = discord.Embed(title=title, description=des)
    await client.edit_message(tmp, embed=mes)

async def private(message):
    await client.send_message(message.channel, 'Starting Private Message')
    await client.send_message(message.author, 'Private Message here')

async def player(message):
    tmp = await client.send_message(message.channel, 'Finding Player...')
    name = message.content.replace('!player ', '')
    try:
        des = playerData.print_status(name)
    except:
        des = 'Your command is wrong'
    await client.edit_message(tmp, des)

async def help_message(message):
    help_mes = '!points {player name} - player average points per game'
    help_mes = help_mes + '\n' + '!points {player name} {week #} - player points for week'
    help_mes = help_mes + '\n' + '!abbrevs - all team abbreviations'
    help_mes = help_mes + '\n' + '!assets {Abbrev} - all draft picks'
    help_mes = help_mes + '\n' + '!roster {Abbrev} - full roster'
    help_mes = help_mes + '\n' + '!roster {Abbrev} {position/TAXI/IR/R} - specific position'
    help_mes = help_mes + '\n' + '!private - start private message with bot'
    help_mes = help_mes + '\n' + '!player {name} - check which team player is on'
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
    elif message.content.startswith('!roster'):
        await roster(message)
    elif message.content.startswith('!help'):
        await help_message(message)
    elif message.content.startswith('!dez'):
        await dez(message)
    elif message.content.startswith('!private'):
        await private(message)
    elif message.content.startswith('!player'):
        await player(message)

client.loop.create_task(quarter_hourly_background_task())
client.run(config.token)
