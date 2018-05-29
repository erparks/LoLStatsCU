def lp_from_league(league_data):
    
    tier = league_data['tier']
    rank = league_data['rank']
    lp   = int(league_data['leaguePoints'])

    return lp_from_tier(tier) + lp_from_rank(rank) + lp

def get_5x5_summonersrift_ranked(league_data):
    for league in league_data:
        if league['queueType'] == 'RANKED_SOLO_5x5':
            return league

def lp_from_tier(tier):
    if tier == 'CHALLENGER' or tier == 'MASTER':
        return 2500
    elif tier == 'DIAMOND':
        return 2000
    elif tier == 'PLATINUM':
        return 1500
    elif tier == 'GOLD':
        return 1000
    elif tier == 'SLIVER':
        return 500
    elif tier == 'BRONZE':
        return 0

def lp_from_rank(rank):
    if rank == 'I':
        return 400
    elif rank == 'II':
        return 300
    elif rank == 'III':
        return 200
    elif rank == 'IV':
        return 100
    else:
        return 0
