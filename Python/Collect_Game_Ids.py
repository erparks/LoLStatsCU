import requests
import json
import pprint
import time
import pandas as pd

SHIP_ID = '19967304'
SHIP_ACC_ID = '32746443'

QTPIE_ACC_ID = '32639237'
api_key = 'RGAPI-4e29693a-7d26-4178-93aa-ff0756eb06ee'

ACC_ID = QTPIE_ACC_ID
game_ids = []



def get_game_ids_by_sum_id(sum_id):
    print(len(game_ids))
    beginIdx = 0
    while True:
     
        url = 'https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/'+str(int(sum_id))+'?beginIndex='+str(beginIdx)+'&queue=420&api_key='+api_key
        
        r = requests.get(url)
        data = json.loads(r.text)
        

        if 'matches' in data:
            for match in data['matches']:
                game_id = match['gameId']
                if game_id not in game_ids and match['queue'] == 420:
                    game_ids.append(game_id)
            if len(data['matches']) == 0:
                break
            
            beginIdx = beginIdx + 100
                
        else:
            print(r.text)
            if r.status_code == 500:
                continue
            print('Waiting for rate limit :' + r.headers['Retry-After'])
            time.sleep(int(r.headers['Retry-After']))


game_file = open('challenger_games.csv', 'w+')

ids = pd.read_csv('challenger_summoner_ids.csv')

ids_read = 0
for sum_id in ids:
    ids_read = ids_read + 1
    print('new id: ' + str(sum_id) + ' -- number ' + str(ids_read))
    get_game_ids_by_sum_id(sum_id)


print len(game_ids)



for game in game_ids:
    game_file.write(str(game) + ', ')


