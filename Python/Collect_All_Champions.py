from pymongo import MongoClient
import Riot_API_Calls as api
import sys

if __name__ == "__main__":
    client = MongoClient()
    db = client['LoLStats']

    api.set_api_key(sys.argv[1])
    champion_collection = db['champions']

    champions = api.get_champions()

    champion_collection.insert(champions)
