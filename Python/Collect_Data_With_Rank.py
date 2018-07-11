from pymongo import MongoClient
import Riot_API_Calls as api
import Riot_Util as util
import Constants as const
import json
import random
import time
import sys

TEST_GAME_ID = '2793274239'
TEST_ACCOUNT_ID = '32639237'

REGION = ''

def get_participant(game, id):
    for participant in game['participants']:
        if participant['participantId'] == id:
            return participant


def process_raw_game(game):
    league_ids = {}
    ranked_players = 0
    game['averageLp'] = 0
    
    for summoner in game['participantIdentities']:
        player = summoner['player']
        print('looking at account id: ' + str(player['accountId']))
        player['participantId'] = summoner['participantId']

        #append the participant dictionary to the player
        player = {**get_participant(game, summoner['participantId']), **player}

        league = api.get_league_by_summoner_id(player['summonerId'])

        ranked_sr_league = util.get_5x5_summonersrift_ranked(league)

        if ranked_sr_league is None:
            continue

        #add current player's league id to the set which is returned
        print('adding league id to recently seen list: ' + str(ranked_sr_league['leagueId']))
        league_ids.setdefault(ranked_sr_league['tier'],[]).append(ranked_sr_league['leagueId'])

        #Count number of games player has on current champion
        champ_id = player['championId']
        curr_player_matchlist = api.get_matchlist_by_acc_id(player['accountId'], 0, champ_id)
        if 'matches' not in curr_player_matchlist:
            return None, None
        total_games = len(curr_player_matchlist['matches'])
        player['matchesOnChampion'] = total_games
        
        #House keeping for lp tracking
        ranked_players += 1
        player['currentLp'] = util.lp_from_league(ranked_sr_league)
        summoner = player
        game['averageLp'] += player['currentLp']
        game['Region'] = REGION

    if ranked_players > 0:
        game['averageLp'] /= ranked_players
    else:
        game['averageLp'] = 0

    game.pop('participants')

    return game, league_ids

def process_timeline(timeline):
    player_frames = {}
    event_frame = {}

    #Iterate over frames
    for frame in timeline['frames']:
        #Iterate over the participants in each frame
        for participant_id, participantFrame in frame['participantFrames'].items():
            #Iterate over the events relavant to the current participant
            # in the current frame and add them to the participants object
            for event in frame['events']:
                if 'participantId' in event and int(event['participantId']) == int(participant_id):
                    participantFrame.setdefault('events', []).append(event)
                    
            participantFrame['timestamp'] = frame['timestamp']
            player_frames.setdefault(participant_id, []).append(participantFrame)
        
    return player_frames, timeline['frameInterval']

def get_next_game_id():
    
    while(True):
        #Choose random tier
        new_tier = random.choice(util.TIERS)
        print (new_tier)
        potential_leagues = leagues_collection.aggregate([
            {'$match': {'tier': new_tier}},
            {'$project': {'leagueIds':1, 'numberOfLeagues': {'$size': '$leagueIds'}}}])

        next_league_id = ''
        
        if potential_leagues.alive:          
            #Choose random league
            for doc in potential_leagues:
                next_league_id = random.choice(doc['leagueIds'])
                print(next_league_id)
                break  
        else:
            challenger_league = api.get_challenger_league()
            next_league_id = challenger_league['leagueId']
            print("Using challenger unti a new league is found")
            #print(challenger_league)
            print(next_league_id)

        
        #Get random player's matchlist from league chosen above
        next_league = api.get_league_by_id(next_league_id)
        next_player = random.choice(next_league['entries'])
        next_player_summoner_id = next_player['playerOrTeamId']
        next_account = api.get_account_from_summoner_id(next_player_summoner_id)
        next_account_id = next_account['accountId']
        next_matchlist = api.get_matchlist_by_acc_id(next_account_id, 0)
        
        #Get first game that hasn't been collected from the player's matchlist
        for game in next_matchlist['matches']:
            game_id = game['gameId']
            print('Looking for game: ' + str(game_id))
            if game['queue'] == 420 and int(time.time()) - game['timestamp'] <= const.WEEK:
                game_already_checked = games_collection.find(
                    {"gameId": { '$exists' : 'true', '$eq': game_id}})
                if game_already_checked.count() == 0:
                    return game_id
            elif int(time.time()) - game['timestamp'] > const.WEEK:
                print("Game too old")

def crawl():
    
    while(True):
        #Collect data
        curr_game_id = get_next_game_id()
        print('Collecting data on ' + str(curr_game_id))
        game = api.get_match_by_id(curr_game_id)
        timeline  = api.get_timeline(curr_game_id)
        
        processed_game, league_ids = process_raw_game(game)

        if processed_game is None:
            continue
        
        processed_timeline, frame_rate = process_timeline(timeline)

        if processed_timeline is None:
            continue
        
        #Combine the timeline and game data
        for player in game['participantIdentities']: 
            player['timeline'] = processed_timeline[str(player['participantId'])]

        processed_game['frameInterval'] = frame_rate

        #Write the game to the db
        games_collection.insert(processed_game)

        #Write the leagues to the db
        for tier, ids in league_ids.items():
            lp = util.lp_from_tier(tier)
            print("Checking tier " + str(tier))
            leagues_collection.update(
                {'tier': tier, 'LP': lp},
                {'$addToSet': { 'leagueIds': {'$each': ids } } },
                upsert=True)


if __name__ == "__main__":
    client = MongoClient()
    db = client['LoLStats']

    api.set_api_key(sys.argv[1])
    api.set_region(sys.argv[2])
    REGION = sys.argv[2]
    games_collection = db['games'+REGION]
    leagues_collection = db['leagues'+REGION]

    crawl()
