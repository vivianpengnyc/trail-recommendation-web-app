import pymongo
import pprint
import json
import numpy as np


# Connect to the mongoDB
pp = pprint.PrettyPrinter(indent=4)
client = pymongo.MongoClient("mongodb://user1:dva2020!@35.227.61.30/outdoor")
db = client['outdoor']

# Extract our 2 collections
hp_collection = db['hikingproject']
at_collection = db['all_trails']

# Extract data from each collection, each document is an item in a list
all_hp = [doc for doc in db.hikingproject.find({})]
all_at = [doc for doc in db.all_trails.find({})]

#############################################################################
# ALIGNMENT: Rename the HP 'Description' /'summary' field to 'description" to match AT
for trail in all_hp:
    # Rename summary to description - only text that is nicely formatted
    trail['description'] = trail.pop('summary')
    # Store the info that is in the Description field in the summary field
    trail['summary'] = trail.pop('Description')

#############################################################################
# ALIGNMENT: Rename the HP 'length' field to 'length_mi" to match AT
for trail in all_hp:
    # Rename length to length_mi
    trail['length_mi'] = trail.pop('length')

#############################################################################
# ALIGNMENT: Match HP location to AT by putting into a dict
for trail in all_hp:
    city_state = trail.pop('location').split(',')
    loc_dict = {}
    loc_dict['latitude'] = trail.pop('latitude')
    loc_dict['longitude'] = trail.pop('longitude')
    loc_dict['state'] = city_state[1].strip().lower()
    trail['location'] = loc_dict

#############################################################################
# PATCH: Attach comments to HP trails
def clean_comments(comments):
    ''' Returns cleaned comments. Comments import as a string,
        list properties are lost - remove remnants '''
    comments = comments.replace('[', '').replace(']', '')
    comments = comments.replace("'", "").replace('"', '')
    comments = comments.replace('\\n', '')
    return comments.strip()
# Load the comments file from Vivian
c_file = 'comments.json'
with open(c_file, encoding='utf-8') as f:
    hp_comments = json.load(f)
# Restructure dict so that it's trail_id (int):comments (str)
nice_dict = {}
for idx, hp_trail_id in hp_comments['trail_id'].items():
    comments = hp_comments['comments'][idx]
    if comments:
        comments = clean_comments(comments)
    nice_dict[hp_trail_id] = comments
# Remove keys if they don't have any comments
nice_dict = {k: v for k, v in nice_dict.items() if v}
# Update the HP trails with the correct comments
for trail in all_hp:
    trail_id = trail['_id']
    if trail_id in nice_dict.keys():
        trail['comments'] = nice_dict[trail_id]
    if trail_id in [4,83,138,227,406]:
        # Annoying fix, 5 trails are unlike any others
        fake_id = '7'+ str(trail_id) + '00000' # checked that these all don't already exist
        trail['_id'] = int(fake_id[:7])

#############################################################################
# Handle import of duplicate trails and some fixes

# Import the json file with duplicate trails knowledge
d_file = 'HP_AT_matching_trails.json'
with open(d_file,encoding='utf-8') as f:
    dup_trails = json.load(f)

# PATCH: Remove matches that don't actually have a valid location
removed_loc_count =0
for hp_id, matches in dup_trails.items():
    for idx, match in enumerate(matches):
        if match['dist_km'] ==0:
            at_trail = all_at[match['AT_idx']]
            if 'latitude' not in at_trail['location'].keys():
                removed = matches.pop(idx)
                print("Removed match for:",hp_id, removed)
                removed_loc_count += 1
    dup_trails[hp_id] = matches

# PATCH: Remove matches that have a FW score below 80
removed_score_count = 0
for hp_id, matches in dup_trails.items():
    for idx, match in enumerate(matches):
        if match['FW_score'] < 80:
            removed = matches.pop(idx)
            print("Removed match for:",hp_id, removed)
            removed_score_count += 1
    dup_trails[hp_id] = matches
# Remove keys if they don't have matching trails
dup_trails = {k: v for k, v in dup_trails.items() if v }

# PATCH: Identify the best match when there are multiple results
multiple_matches =0
for hp_id, matches in dup_trails.items():
    if len(matches) > 1:
        # Find all scores within 5 pts from top score
        scores = np.array([trail['FW_score'] for trail in matches])
        diff = scores - scores[0]
        close_scores_idx = np.where(np.abs(diff) <= 5)[0]

        # If there are multiple close scores, choose the one with smallest distance
        if len(close_scores_idx) > 1:
            # Find minimum distance out of the closest scores
            dists = np.array([matches[idx]['dist_km'] for idx in close_scores_idx])
            min_dist_idx = np.argmin(dists)

            # Best match is closest trail
            best_match_idx = close_scores_idx[min_dist_idx]
            if best_match_idx != 0:
                print(f'Max score for {hp_id} match is {matches[0]}, but best trail is {matches[best_match_idx]}')
        else:
            best_match_idx = close_scores_idx[0]
        dup_trails[hp_id] = [matches[best_match_idx]]
        multiple_matches += 1

# double check all trails only have 1 match
for hp_id, matches in dup_trails.items():
    if len(matches) > 1:
        print("Oh no!")

#############################################################################
# Join the HP and AT data when relevant

def attach_at_info(hp_trail_dict, at_matching_trail_dict):
    # Removes the all trail from all_at and attaches it to HP trail
    if 'tags' in at_matching_trail_dict.keys():
        hp_trail_dict['tags'] = at_matching_trail_dict['tags']

    if 'reviews' in at_matching_trail_dict.keys():
        hp_trail_dict['reviews'] = at_matching_trail_dict['reviews']

    hp_trail_dict['AT_matched'] = True
    return hp_trail_dict


# Attach AT info to the HP trails
joined = 0
for trail in all_hp:
    trail_id = str(trail['_id'])
    if (trail_id in dup_trails.keys()) & ('AT_matched' not in trail.keys()):
        matching_trail = dup_trails[trail_id][0]
        matching_trail_info = all_at[matching_trail['AT_idx']]
        trail = attach_at_info(trail, matching_trail_info)
        joined += 1

# Remove the matched trails and create a subset of AllTrails data
remove_indices = { dup_trails[trail][0]['AT_idx'] for trail in dup_trails}
subset_at = [i for j, i in enumerate(all_at) if j not in remove_indices]

# Join the full hp and subset of at, 2 lists
joined_data = all_hp + subset_at

#########################################################################################
# THE BELOW WILL MODIFY THE MONGODB COLLECTION, DO NOT UNCOMMENT UNLESS NECESSARY
#########################################################################################
# # Upload the data to mongoDB
#
# # If collection already exists, drop it and open a new collection
# db.trails.drop()
# joined_collection = db['trails']
#
# # Insert the data into the trails collection
# joined_collection.insert_many(joined_data)
# print("Done, uploaded!")