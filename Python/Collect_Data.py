import requests
import json
import time
import pandas as pd
from sqlalchemy import create_engine


api_key = 'RGAPI-be7aca61-01f6-4642-9176-bf12d069270e'

def get_timeline(game_id):
    url = 'https://na1.api.riotgames.com/lol/match/v3/timelines/by-match/'+ str(game_id)+'?api_key=' + api_key
    r = requests.get(url)
    data = json.loads(r.text)

    if 'frames' in data:
        game_file = open('Timelines/'+str(game_id)+'.json', 'w+')
        game_file.write(r.text)
        game_file.close()
    else:
        print(r.text)
        if r.status_code == 500 or r.status_code == 404:
            print '^^ When looking for game_id: ' + str(game_id)
            return
        elif r.status_code == 503:
            print('Service Unavailable Received. Waiting 5 minutes.')
            time.sleep(300)
            get_timeline(game_id)
            
        print('Waiting for rate limit :' + r.headers['Retry-After'])
        time.sleep(int(r.headers['Retry-After']))
        get_timeline(game_id)

        
df = pd.read_csv('challenger_games.csv', sep = ',', header = None)
print df.as_matrix()

game_ids =  df.as_matrix()[0][101022:]
for game_id in game_ids:
    get_timeline(int(game_id))
