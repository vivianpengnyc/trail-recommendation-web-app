"""
REST API Resource Routing
http://flask-restplus.readthedocs.io
"""

from datetime import datetime
from flask import request
from flask_restplus import Resource
import pymongo
import random
import pickle
import os
import sys
import json

from .security import require_auth
from . import api_rest

from .geocode import Geocode
from .TrailScoring import TrailScorer

@api_rest.route('/get_location/')
class Location(Resource):
    """ Return location test """
    def get(self):
        location = request.args.get('location')
        return {'test': location}, 201

@api_rest.route('/run_model/')
class Model(Resource):
    """ 
    Run model. MongoDB connection is established. Trails are filtered using ArcGIS
    Geocoding API. Filtered trails are fed through model. Recommended trail and data
    is returned.
    """

    def __init__(self, request):
        self.CONNECTION = 'mongodb://user1:dva2020!@35.227.61.30/outdoor'
        self.path_to_tfidf_vect = './app/pickle/tfidf_model.sav'
        self.path_to_doc_matrix = './app/pickle/sparse_matrix.npz'

    def get(self):
        self.text = request.args.get('text')
        self.miles = float(request.args.get('miles'))
        self.park = request.args.get('park')
        self.length = float(request.args.get('length'))
        self.difficulty = request.args.get('difficulty')

        with pymongo.MongoClient(self.CONNECTION) as client:
            db = client['outdoor'].trails
            coordinates, filtered_trails = self.filter_location(db)
            model_dict = self.score_model(filtered_trails)
            model_ids = model_dict.keys()
            results = []

            for trail in filtered_trails:
                if trail['_id'] in model_ids:

                    longitude = trail['location']['longitude']
                    latitude = trail['location']['latitude']
                    g_maps = f'http://www.google.com/maps/place/{latitude},{longitude}'

                    sub_dict = {}
                    sub_dict['id'] = trail['_id']
                    sub_dict['name'] = trail['name']
                    sub_dict['score'] = model_dict[trail['_id']]
                    sub_dict['difficulty'] = trail['difficulty_map']
                    sub_dict['map'] = g_maps
                    sub_dict['description'] = trail['description']
                    sub_dict['elevation'] = trail.get('elevation_gain_ft', trail.get('ascent', 0))
                    sub_dict['length'] = trail['length_mi']
                    sub_dict['loc'] = trail['loc']
                    sub_dict['url'] = trail['url']
                    results.append(sub_dict)
            trails = sorted(results, key=lambda x: x['score'], reverse=True)
            result_dict = {
                'coordinates': coordinates,
                'results': trails
            }
        return result_dict, 201

    def filter_location(self, db):
        """Run spatial query in MongoDB and return within specified radius of given location."""
        geocode = Geocode(self.park)
        geocode.get_token()
        longitude, latitude = geocode.geocode_address()
        distance = 1/3858.8 * self.miles
        query = {
            'loc': {
                '$geoWithin': {
                    '$centerSphere': [[longitude, latitude], distance]
                }
            }
        }
        params ={
            'reviews': 0,
        }
        filtered_trails = [trail for trail in db.find(query, params)]
        return [longitude, latitude], filtered_trails
    
    def score_model(self, trails, num_trails=25):
        """Score input trails and return trails"""
        user_data = {
            'length': self.length,
            'difficulty': self.difficulty,
            'query': self.text
        }
        model = TrailScorer(self.path_to_tfidf_vect, self.path_to_doc_matrix, user_data)
        scores = [tuple(x) for x in model.score_many(trails).items()]
        scores = dict(sorted(scores, key=lambda x: x[1], reverse=True))
        return scores