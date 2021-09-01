import pymongo
import pprint
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from math import sin, cos, sqrt, atan2, radians, floor


def top_fw_matches(hp_name, at_names):
    ''' Takes 1 HP trail, and finds trails from AT with similar names
    Returns: list of tuples [(AT Trail Name, Similarity Score, AT _id),...]
    Assumption: scorer=token_sort_ratio score; limit of 20 trails; default threshold of 70
    '''
    matches = process.extractBests(hp_name, at_names,
                                   scorer=fuzz.token_sort_ratio, limit=100,
                                   score_cutoff = 70)
    return matches

def distance(lat1,lon1,lat2,lon2):
    ''' Calculate the Haversine distance
    Returns
    d : float (distance in km)
    '''
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    R = 6373.0  # km
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c
    return d

def calc_dist(hp_trail, at_trail):
    ''' Calc distance between 1 HP trail and 1 AT trail'''
    try:
        hp_lat = hp_trail['latitude']
        hp_lon = hp_trail['longitude']

        at_lat = at_trail['location']['latitude']
        at_lon = at_trail['location']['longitude']

        return distance(hp_lat,hp_lon,at_lat,at_lon)
    except:
        return 0 # Some trails don't have lat/lon

def reduce_matches(hp_trail,at_matches, all_at):
    ''' Takes 1 HP trail, a list of AT matching trails, all the AT trails info, and reduces to those nearby
     Assumption: nearby defined as less than the length of the trail itself '''
    trail_length = hp_trail['length']*1.609344  # convert to km
    reduced_matches = []
    for match in at_matches:
        at_trail = all_at[match[2]]
        dist = calc_dist(hp_trail, at_trail)
        if dist <= trail_length:
            details = {'AT_name':match[0], 'AT_idx':match[2],'FW_score':match[1],'dist_km':dist}
            reduced_matches.append(details)
    return reduced_matches


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    client = pymongo.MongoClient("mongodb://user1:dva2020!@35.227.61.30/outdoor")
    db = client['outdoor']

    hp_collection = db['hikingproject']
    at_collection = db['all_trails']

    all_hp = [doc for doc in db.hikingproject.find({})]
    all_at = [doc for doc in db.all_trails.find({})]
    at_names = {idx: trail['name'] for idx, trail in enumerate(all_at)}
    #at_states = {idx: trail['location'] for idx, trail in enumerate(all_at)} #If need to rerun, split by state

    similar_trails = {}

    for trail in all_hp:
        hp_name = trail['name']
        #hp_state = trail['location'].split(',')[1].strip().lower() #If need to rerun, split by state
        print(f'Matching: {hp_name}')
        matches = top_fw_matches(hp_name,at_names)
        if matches:
            reduced_matches = reduce_matches(trail,matches,all_at)
            if reduced_matches:
                similar_trails[trail['_id']] = reduced_matches

    with open('HP_AT_matching_trails.json', 'w') as f:
        json.dump(similar_trails, f)

# # Test single trail
# trail = all_hp[0]
# hp_name = trail['name']
# matches = top_fw_matches(hp_name, at_names)
# reduced_matches = reduce_matches(trail,matches,all_at)
# if reduced_matches:
#     similar_trails[trail['_id']] = reduced_matches
