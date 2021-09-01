import requests
import csv
import math
import pymongo



# Import all the trail ids and concat into single string
with open('HPtrail_ids.csv', mode='r') as file:
    reader = csv.reader(file)
    trail_ids = [row[0] for row in reader]

# Determine how large of batches to run
num_trails = len(trail_ids)
batch_size = 50
batches = math.ceil(num_trails/batch_size)

#initialize
batch_end = 32850
data = []
api_key = 0 #INSERT API KEY HERE
url_domain = 'https://www.hikingproject.com/data/get-trails-by-id'
headers = {"User-Agent":"GeorgiaTechOMSA/1.0 (https://pe.gatech.edu/degrees/analytics)"}
timeout = 30

# Run through each batch call
for i in range(batches):
    batch_start = batch_end
    batch_end = batch_start + batch_size
    print(f'Batch: {i}\n Batch Start: {batch_start}\n Batch End: {batch_end}')
    trails_id_str = ','.join(trail_ids[batch_start:batch_end])

    # Make the request to get trail details by trail ids
    parameters = {'key': api_key, 'ids': trails_id_str}
    r = requests.get(url_domain,params=parameters, headers=headers, timeout=timeout)

    # Extract the trails info and append to data list
    if r.status_code == requests.codes.ok and r.json()['success'] == 1:
        for newdata in r.json()['trails']:
            data.append(newdata)
    else:
        print(f'Request failed: {r.text}')
        break

#########################################################################################
# THE BELOW WILL MODIFY THE MONGODB COLLECTION, DO NOT UNCOMMENT UNLESS NECESSARY
#########################################################################################
# # Open connection to mongodb
# client = pymongo.MongoClient("mongodb://user1:dva2020!@35.227.61.30/outdoor")
# db = client['outdoor']
#
# # If collection exists, drop it and then restart it
# db.hikingproject.drop()
# hp_collection = db['hikingproject']
#
# # Perform modifications to the HP data
# for trail_dict in data:
#     # Rename id to _id to allow use as the mongodb id
#     trail_dict['_id'] = trail_dict.pop('id')
#
# # Insert the data into the fresh hikingproject collection
# hp_collection.insert_many(data)
