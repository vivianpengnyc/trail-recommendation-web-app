import requests
import json

## script geocodes address and creates a buffer of defined distance to intersect w/ points 

class Geocode:

    def __init__(self, address):
        self.address = address

    def get_token(self):
        ''' Return token '''
        try:
            url = "https://www.arcgis.com/sharing/rest/oauth2/token"
            client_id = "gt7uwvWtbWnSVZ2b"
            client_secret = "1fe1b032b11342f8aa6f46b157ff8841"

            payload = "client_id={}&client_secret={}&grant_type=client_credentials".format(client_id,client_secret)
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'accept': "application/json",
                'cache-control': "no-cache",
                'postman-token': "11df29d1-17d3-c58c-565f-2ca4092ddf5f"
            }

            response = requests.request("POST", url, data=payload, headers=headers)
            token = response.json().get('access_token')
        except:
            token = "f7W2nveAsuZ7K9kYKFS-kspOQHu6jBWwXET1V4WtcX5jdG7mMJfA6cKGv21PX9zwtIYLCYbUQ1wTSdGr0PXyQ4wke2zn_VMS7iQjrsGphwgvYUr8g8473ECqwTX1vQvQlo_YmVlxavLmEzdxUWctMg.."
        self.token = token

    def geocode_address(self, outSR="4326"):
        ''' Convert address to longitude and latitude '''
        ## make request to REST API
        url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses?"
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        addresses = json.dumps({ 'records': [{ 'attributes': { 'OBJECTID': 1, 'SingleLine': self.address}}] })
        r = requests.post(url, headers = headers, data = { 'addresses': addresses, 'f':'json', 'token': self.token})
        r = r.json()
        
        ## parse json
        lon = dict(dict(r.get('locations')[0])['location'])['x']
        lat = dict(dict(r.get('locations')[0])['location'])['y']

        return (lon, lat)


    def get_buffer(lat,lon, distance, unit = 9036): 
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Utilities/Geometry/GeometryServer/buffer?f=json&geometries="
        r_url = "{}{},{}&inSR=4326&distances={}&unit={}".format(url,lon,lat,distance,unit)

        r = requests.get(url = r_url)
        return r.json()
