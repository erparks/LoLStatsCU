import requests
import json
import pprint
import time

SHIP_ID = '19967304'
SHIP_ACC_ID = '32746443'

QTPIE_ACC_ID = '32639237'
api_key = 'RGAPI-4e29693a-7d26-4178-93aa-ff0756eb06ee'

ACC_ID = QTPIE_ACC_ID
game_ids = []



def get_game_ids_by_acc_id(acc_id):
    print(len(game_ids))
    beginIdx = 0
    while True:
     
        url = 'https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/'+acc_id+'?beginIndex='+str(beginIdx)+'&api_key='+api_key

        r = requests.get(url)
        data = json.loads(r.text)
        print('Looping... ' + str(r.status_code))
        if r.status_code == '429':
            print('Waiting for rate limit')
            time.sleep(10)
            
        for match in data['matches']:
            game_id = match['gameId']
            if game_id not in game_ids :
                game_ids.append(game_id)

        if len(data['matches']) == 0 or beginIdx == 400:
            break
        beginIdx = beginIdx + 100

def acc_id_from_sum_id(sum_id):

    url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/'+sum_id+'?api_key='+api_key
    r = requests.get(url)
    data = json.loads(r.text)

    if 'accountId' in data:
        return data['accountId']
    else:
        print(r.text)
        
        print('Waiting for rate limit :' + r.headers['Retry-After'])
        time.sleep(int(r.headers['Retry-After']))
        return


#Returns ACCOUNT IDS for challenger players
def get_challenger_summoner_ids():
    summoner_ids = []
    url = 'https://na1.api.riotgames.com/lol/league/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key='+api_key

    r = requests.get(url)
    data = json.loads(r.text)
    
    for entry in data['entries']:
        summoner_ids.append(acc_id_from_sum_id(entry['playerOrTeamId']))
##        if len(summoner_ids) % 99 == 0:
##            print 'sleeping for rate limit. ' + str(len(summoner_ids)) + ' ids retrieved.'
##            time.sleep(91)
    print(summoner_ids)

    return summoner_ids



summoner_ids = get_challenger_summoner_ids()
