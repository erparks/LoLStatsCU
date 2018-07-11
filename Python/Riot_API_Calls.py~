import requests
import json

API_KEY = 'RGAPI-4f9a01e9-3548-4bfa-be3a-250902437b8d'

def __call_api(url):
    r = requests.get(url)
    data = json.loads(r.text)

    if r.status_code == 503:
        print('Service Unavailable Received. Waiting 5 minutes.')
        time.sleep(300)
        return __call_api(url)

    elif r.status_code == 500:
        print('Riot internal server error. Retrying..')
        return __call_api(url)        
    
    elif r.status_code == 429:
        print('Waiting for rate limit :' + r.headers['Retry-After'])
        time.sleep(int(r.headers['Retry-After']))
        return __call_api(url)

    elif r.status_code == 401:
        print(r)
        print('Have you tried refreshing your api key?')
    
    elif not r.status_code == 200:
        print(r)
        print(url)

    return data, r

#https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchTimeline
def get_timeline_by_gameId(game_id):
    url = 'https://na1.api.riotgames.com/lol/match/v3/timelines/by-match/'
    +str(game_id)+'?api_key=' + api_key

    return __call_api(url)

def accountId_from_summonerId(sum_id):
    url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/'+str(sum_id)+'?api_key='+api_key

    return __call_api(url)

def get_matchlist_by_acc_id(acc_id, beginIdx):
     url = 'https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/'+str(acc_id)+'?beginIndex='+str(beginIdx)+'&api_key='+api_key

     return __call_api(url)

#https://developer.riotgames.com/api-methods/#match-v3/GET_getMatch
def get_match_by_id(match_id):
    url = 'https://na1.api.riotgames.com/lol/match/v3/matches/'+str(match_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getLeagueById
def get_league_by_id(league_id):
    url = 'https://na1.api.riotgames.com/lol/league/v3/leagues/'+str(leauge_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getLeagueById
def get_leagueId_by_summonerId(sum_id):
    url = 'https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/'+str(sum_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguePositionsForSummoner
def get_league_by_summonerId(sum_id):
    url = 'https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/'+str(sum_id) +'?api_key='+API_KEY

    return __call_api(url)
