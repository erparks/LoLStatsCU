from pymongo import MongoClient
import Riot_API_Calls as api
import Riot_Util as util

API_KEY = 'RGAPI-4f9a01e9-3548-4bfa-be3a-250902437b8d'

TEST_GAME_ID = '2793274239'
TEST_ACCOUNT_ID = '32639237'

def get_participant(game, id):
    for participant in game['participants']:
        if participant['participantId'] == id:
            return participant


def process_raw_game(game):
    league_ids = {}

    game['averageLp'] = 0
    
    for summoner in game['participantIdentities']:
        player = summoner['player']
        
        #append the participant dictionary to the player
        player = {**get_participant(game, summoner['participantId']), **player}
        
        league, r = api.get_league_by_summonerId(player['summonerId'])

        ranked_sr_league = util.get_5x5_summonersrift_ranked(league)
        
        league_ids.setdefault(ranked_sr_league['tier'],[]).append(ranked_sr_league['leagueId'])
        
        player['currentLp'] = util.lp_from_league(ranked_sr_league)
        game['averageLp'] += player['currentLp']
            
    game['averageLp'] /= len(game['participantIdentities'])
    game.pop('participants')

    return game, league_ids

def crawl(game_id):
    game, r = api.get_match_by_id(TEST_GAME_ID)
    
    processed_game, league_ids = process_raw_game(game)
    
    games_collection.insert(processed_game)

    for tier, ids in league_ids.items():
        leagues_collection.update(
            {'tier': tier, 'LP': util.lp_from_tier(tier)},
            {'$addToSet': { 'leagueIds': {'$each': ids } } },
            upsert=True)
    

    
if __name__ == "__main__":
    client = MongoClient()
    db = client['LoLStats']

    games_collection = db['games']
    leagues_collection = db['leagues']
    
    crawl(TEST_GAME_ID)
