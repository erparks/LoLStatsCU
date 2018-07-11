import requests
import json
import time

API_KEY = ''
REGION = ''

def set_api_key(api_key):
    global API_KEY
    API_KEY = api_key

def set_region(region):
    global REGION
    REGION = region

def __call_api(url):
    r = requests.get(url)
    data = json.loads(r.text)

    print(r)
    
    if r.status_code == 401:
        print('API call failed with 401, try reseting your API key.')
        print(url)
    elif r.status_code == 403:
        print('API call failed with 403, you made a bad call.')
        print(url)
    elif r.status_code == 429:
        if not 'X-Rate-Limit-Type' in r.headers:
            print('Internal rate limiting, waiting 10 minutes...')
            time.sleep(600)
            return __call_api(url)
        else:
            print('Waiting for rate limit, time remaining: ' + r.headers['Retry-After'])
            
            time.sleep(int(r.headers['Retry-After']))
            return __call_api(url)
    elif r.status_code == 500:
        print("Internal RIOT service error, retrying...")
        time.sleep(30)
        return __call_api(url)
    elif r.status_code == 503:
        print('Service Unavailable Received. Waiting 5 minutes.')
        time.sleep(300)
        return __call_api(url)
    elif not r.status_code == 200:
        print(r)
        print(url)
        
    return data

def get_account_from_summoner_id(sum_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/summoner/v3/summoners/'+str(sum_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchlist
def get_matchlist_by_acc_id(acc_id, beginIdx, champ_id = None):    
    if champ_id is None:
     url = 'https://'+REGION+'.api.riotgames.com/lol/match/v3/matchlists/by-account/'+str(acc_id)+'?beginIndex='+str(beginIdx)+'&api_key='+API_KEY
    else:
       url = 'https://'+REGION+'.api.riotgames.com/lol/match/v3/matchlists/by-account/'+str(acc_id)+'?beginIndex='+str(beginIdx)+'&champion='+str(champ_id)+'&api_key='+API_KEY 

    return __call_api(url)


#https://developer.riotgames.com/api-methods/#match-v3/GET_getMatch
def get_match_by_id(match_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/match/v3/matches/'+str(match_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getLeagueById
def get_league_by_id(league_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/league/v3/leagues/'+str(league_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getLeagueById
def get_leagueId_by_summoner_id(sum_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/league/v3/positions/by-summoner/'+str(sum_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguePositionsForSummoner
def get_league_by_summoner_id(sum_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/league/v3/positions/by-summoner/'+str(sum_id) +'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchTimeline
def get_timeline(game_id):
    url = 'https://'+REGION+'.api.riotgames.com/lol/match/v3/timelines/by-match/'+str(game_id)+'?api_key='+API_KEY

    return __call_api(url)

#https://developer.riotgames.com/api-methods/#lol-static-data-v3/GET_getChampionList
def get_champions():
    url = 'https://'+REGION+'.api.riotgames.com/lol/static-data/v3/champions?locale=en_US&dataById=false&api_key='+API_KEY

    return __call_api(url)

def get_challenger_league():
    url = 'https://'+REGION+'.api.riotgames.com/lol/league/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key='+API_KEY

    return __call_api(url)
