from pymongo import MongoClient
import Riot_API_Calls as api
import Riot_Util as util
import Constants as const
import json
import random
import time
import sys
import pprint

TEST_GAME_ID = '2793274239'
TEST_ACCOUNT_ID = '32639237'

REGION = ''

def get_participant(game, id):
    for participant in game['participants']:
        if participant['participantId'] == id:
            return participant

def get_team(game, team_id):
    for team in game['teams']:
        if team['teamId'] == team_id:
            return team

def get_playerDTO(game, participant_id):
    for participant_identity in game['participantIdentities']:
        if participant_identity['participantId'] == participant_id:
            return participant_identity['player']
        
def process_raw_game(game):
    league_ids = {}
    participant_summoner_ids = {}
    ranked_players = 0
    winning_team = ''
    game['averageLp'] = 0

    for team in game['teams']:
        if team['win'] == 'Win':
            game['winner'] = team['teamId']
            winning_team = team['teamId']
        team['players'] = []

    for summoner in game['participantIdentities']:
        participant_summoner_ids[summoner['participantId']] = summoner['player']['summonerId']
        
    for participant in game['participants']:

        #Win
        participant['win'] = 'Win' if participant['teamId'] == winning_team else 'Fail'
        
        #Summoner ID
        participant['summonerId'] = participant_summoner_ids[participant['participantId']]

        #Account ID
        account_DTO = api.get_account_from_summoner_id(participant['summonerId'])
        participant['accountId'] = account_DTO['accountId']

        #Team
        team = get_team(game, participant['teamId'])
        team['players'].append(participant)

        #PlayerDTO
        participant['playerDTO'] = get_playerDTO(game, participant['participantId'])
        
        #Count number of games player has on current champion
        champ_id = participant['championId']
        curr_player_matchlist = api.get_matchlist_by_acc_id(participant['accountId'], 0, champ_id)
        if 'matches' not in curr_player_matchlist:
            return None, None
        total_games = len(curr_player_matchlist['matches'])
        participant['matchesOnChampion'] = total_games


        #This comes last
        #Current LP
        league = api.get_league_by_summoner_id(participant['summonerId'])
        ranked_sr_league = util.get_5x5_summonersrift_ranked(league)
        if ranked_sr_league is None:
            continue
        
        participant['currentLP']  =  util.lp_from_league(ranked_sr_league)

        #add current player's league id to the set which is returned
        league_ids.setdefault(ranked_sr_league['tier'],[]).append(ranked_sr_league['leagueId'])
        
        #House keeping for lp tracking
        ranked_players += 1
        participant['currentLp'] = util.lp_from_league(ranked_sr_league)
        game['averageLp'] += participant['currentLp']

    if ranked_players > 0:
        game['averageLp'] /= ranked_players
    else:
        game['averageLp'] = 0


    return game, league_ids

######################################################
#
# Create list of events and MatchParticipantFrameDtos
#
######################################################
def process_timeline(timeline):
    player_frames = {}
    event_frames = {}

    #Iterate over frames
    for frame in timeline['frames']:
        #Iterate over the participants in each frame
        for participant_id, participantFrame in frame['participantFrames'].items():
            #Create list of events by participantId
            for event in frame['events']:
                if 'participantId' in event:
                    event['timestamp'] = frame['timestamp']
                    event_frames.setdefault(event['participantId'], []).append(event)
            #Create list of MatchParticipantFrameDTOs
            participantFrame['timestamp'] = frame['timestamp']
            player_frames.setdefault(participantFrame['participantId'], []).append(participantFrame)
        
    return player_frames, event_frames, timeline['frameInterval']

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

        #Process game
        processed_game, league_ids = process_raw_game(game)

        if processed_game is None:
            continue

        #Process timeline
        player_frames, event_frames, frame_rate = process_timeline(timeline)

        if player_frames is None:
            continue

        #Add timeline data to the participants
        for participant in processed_game['participants']:
            participant['events'] = event_frames[participant['participantId']]
            participant['frames'] = player_frames[participant['participantId']]

        #Add the frame interval to the game
        processed_game['frameInterval'] = frame_rate

        print(json.dumps(game, indent=4, sort_keys=True))

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
    db = client['LoLData']
    leagueDB = client['LoLStats']
    api.set_api_key(sys.argv[1])
    api.set_region(sys.argv[2])
    REGION = sys.argv[2]
    games_collection = db['games'+REGION]
    leagues_collection = leagueDB['leagues'+REGION]

    crawl()
