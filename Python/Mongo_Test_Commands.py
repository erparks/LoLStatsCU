from pymongo import MongoClient
from pprint import pprint
import json

client = MongoClient()
db = client['LoLData']

games_collection = db['gamesNA1']

cursor = games_collection.aggregate([
    {
	'$project':
	{
	    'participantIdentities':
	    {	
		'$filter':
		{
		    'input':"$participantIdentities",
		    'as':"identity",
		    'cond':
		    {
			'$eq': ["$$identity.participantId", 2]
		    }
		    
		}
	    },
            'participantIdentities' : { 'timeline':0}
	    
	}
	
	
    }
    
]
)

cursor = games_collection.find({},{"teams":1})


for document in cursor: 
    for key, value in document.items():
        if key == "teams":
            for obj in value:
                print(type(obj['players'][0]))
                for pkey, pval in obj['players'][0].items():
                    print(pkey)
                    
