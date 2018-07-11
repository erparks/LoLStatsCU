from pymongo import MongoClient
from pprint import pprint

client = MongoClient()
db = client['LoLStats']

games_collection = db['games']

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


for document in cursor: 
    pprint(document)
