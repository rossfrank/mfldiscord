import config
import requests

def api_request(request, params=''):
    if params:
        params = '&' + params
    link = 'http://www' + config.server + '.myfantasyleague.com/' + config.year + '/export?TYPE=' + request + '&L=' + config.league_id + '&APIKEY=' + config.api_key + params +'&JSON=1'
    print(link)
    return(requests.get(link).json())

"""
updated at most once per day
format:
    {timestamp, since, player:[{position, name, id, team},...]}
"""
def get_players():
    return(api_request('players')['players'])

"""
format:
    {currentWaiverType, playerLimitUnit, taxiSquad, endWeek,
    maxWaiverRounds, lockout, nflPoolStartWeek,
    franchises:{count, franchise:
        [{abbrev, division, mail_type, name, future_draft_picks, waiverSortOrder,
        username, lastVisit, email, time_zone, id, play_audio, use_advanced_editor,
        owner_name, mail_event},...]},
    standingsSort, draftPlayerPool, id, nflPoolType,
    history, rosterSize, name, draftLimitHours,
    starters:{count, position:[{name, limit},...], idp_starters},
    nflPoolEndWeek, bestLineup, precision, lastRegularSeasonWeek, survivorPool,
    usesContractYear, injuredReserve, startWeek, commish_username,
    survivorPoolStartWeek, usesSalaries, baseURL,
    divisions:{count, division[{name, id},...]}, loadRosters}
"""
def get_league():
    return(api_request('league')['league'])

"""
passed franchise is four digits
format:
    if franchise is passed:
        {franchise: {player:[{status, id},...],id}}
    no franchise is passed:
        {franchise: [{player:[{status, id},...],id},...]}
"""
def get_roster(franchise = ''):
    if franchise:
        franchise = "&FRANCHISE=" + franchise
    return(api_request('rosters', franchise)['rosters'])

"""
gets trades pending league approval
format:
    if one trade:
    {pendingTrade:{offeredto, will_give_up, offeringteam,
                   comments, description, will_receive, expires}}
    if multiple trades:
    {pendingTrade:[{offeredto, will_give_up, offeringteam,
                   comments, description, will_receive, expires},...]}

"""
def get_pending_trades():
    return(api_request('pendingTrades','FRANCHISE_ID=0000')['pendingTrades'])

"""
format:
    {franchise:[{futureYearDraftPicks, currentYearDraftPicks,players,id},...]}
"""
def get_assets():
    return(api_request('assets')['assets'])

"""
When set, this will also return draft picks offered.
Current year draft picks look like DP_02_05
which refers to the 3rd round 6th pick
(the round and pick values in the string are one less than the actual round/pick).
For future years picks, they are identified like FP_0005_2018_2
where 0005 referes to the franchise id who originally owns the draft pick,
then the year and then the round (in this case the rounds are the actual rounds, not one less).

format:
    {tradeBait:[{timestamp, franchise_id, willGiveUp, inExchangeFor},...]}
"""
def get_trade_bait(picks = 'yes'):
    return(api_request('tradeBait','INCLUDE_DRAFT_PICKS=' + picks)['tradeBaits'])

"""
if no week passed then gives all bye weeks
format:
    {"week", "team":[{"bye_week,"id"},...],"year"}
"""
def get_bye_weeks(week = ''):
    if week:
        week = "&W=" + week
    return(api_request('nflByeWeeks',week)['nflByeWeeks'])

"""
if week is empty take the average
format:
    {playerScore: {week, score, id}}
"""
def get_player_score(player, week = 'AVG'):
    y = config.year
    params = '&W=' + week + '&YEAR=' + y + '&PLAYERS=' + player + '&RULES=yes'
    return(api_request('playerScores', params)['playerScores'])

"""
format:
    {draftUnit: {unit, draftType, round1DraftOrder, draftPick: [{timestamp,franchise,round,pick,player,comments},...]}}
"""
def get_draft_results():
    return(api_request('draftResults')['draftResults'])
