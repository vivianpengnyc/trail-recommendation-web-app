#!/usr/bin/env python3

'''
Creates a fields in MongoDB to support similarity scoring.
Creates:
{'difficulty_map' : a single field for difficulty, currently just maps HP/AT ratings
'tokenized_text' : all the relevant text of a trail, cleaned and tokenized,
'index' : essentially the row number of the trail in the mongoDB collection,
'keywords' : Top n keywords for that trail, per tfidf vector,
'tfidf_vec' : A vector of important words and their weights}
'''

import pymongo
import time
import pickle
import re
import numpy as np
import string
from nltk.tokenize import RegexpTokenizer
from nltk.probability import FreqDist
from scipy import sparse
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer


def map_difficulty(trail_dict):
    '''Create a single difficulty score
    From HP website:
    green: Easy
    greenBlue: Easy / Intermediate
    blue: Intermediate
    blueBlack: intermediate / difficult
    black: difficult
    dblack: very difficult

    From AT website:
    easy
    moderate
    hard

    Both:
    missing
    '''
    map_dict = {'green': 'Easy',
               'greenBlue': 'Easy',
               'easy': 'Easy',
               'blue': 'Intermediate',
               'blueBlack': 'Intermediate',
               'moderate': 'Intermediate',
               'black': 'Difficult',
               'dblack': 'Difficult',
               'hard': 'Difficult'}
    try:
        return map_dict[trail_dict['difficulty']]
    except:
        return 'Unknown'


def join_all_text_field(trail_dict):
    ''' Append a field that is a long string of all the different text for the trail'''
    if 'description' in trail_dict.keys() and trail_dict['description']:
        all_text = trail_dict['description']
    else:
        all_text = ' '

    if 'summary' in trail_dict.keys() and trail_dict['summary']:
        all_text += ' '
        all_text += trail_dict['summary']

    if 'overview' in trail_dict.keys():
        all_text += ' '
        all_text += trail_dict['overview']

    if 'comments' in trail_dict.keys():
        all_text += ' '
        all_text += trail_dict['comments']

    if 'reviews' in trail_dict.keys():
        for review in trail_dict['reviews']:
            if 'text' in review.keys():
                all_text += ' '
                all_text += review['text']

    return all_text


def clean_text(text):
    ''' Clean the input text for grammar, punctuation, capitals, etc'''
    text = text.replace('\n', '')
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text.lower())  # remove punctuations with a white space
    #text = re.sub('\w*\d\w*', ' ', text) # This one increases the time to run 5x. Tokenizer removes nums anyway.

    text = text.replace(' n ', '')
    text = text.replace('\r', '')

    return text.strip()


def tokenize_string(text_str):
    ''' Break a full string doc into words '''

    cap_tokenizer = RegexpTokenizer("[a-z]['\w]+") # only keep the words not numbers
    text_li = cap_tokenizer.tokenize(text_str)

    return text_li


def remove_stopwords(text_li):
    ''' remove the stopwords from full string'''

    custom_words = ["usfs", "trail", "trails", "hike", "mile"]

    my_stop_words = text.ENGLISH_STOP_WORDS.union(custom_words)

    filtered_text_li = [w for w in text_li if not w in my_stop_words]

    return filtered_text_li


def lem_stem(text, method = 'lem'):
    ''' Lemmetize text '''
    pass


def tfidf(corpus, ngram_range = (1,1)):
    ''' Perform tfidf on the input text vector
        input:
            row_document
        output:
            tfidf_vectorizer (a fitted vectorizer to be used for use later)
            X (sparse matrix that each row represent each trail)
    '''

    # Initialize and train on corpus
    tfidf = TfidfVectorizer(ngram_range=ngram_range)
    tfidf_vectorizer = tfidf.fit(corpus)

    # Transform corpus into sparse tfidf matrix
    X = tfidf_vectorizer.transform(corpus)

    return tfidf_vectorizer, X


def get_top_keywords(tfidf_feature_names_array, tfidf_vector, n):
    ''' Returns the top n keywords for a single document based on tfidf vector '''

    # Sort the tfidf vector, from most to least relevant (returns their indices)
    tfidf_sorting = np.argsort(tfidf_vector.toarray()).flatten()[::-1]

    # Extract the keywords at these indices
    top_n_keywords = tfidf_feature_names_array[tfidf_sorting[:n]]

    return top_n_keywords.tolist()

def csr_todict(csr_vec):
    ''' Converts a scipy.sparse.csr.csr_matrix to a dict of components
     How to reconstruct tfidf vector later:
        csr_matrix((data,indices,indptr),shape=shape)'''
    data = csr_vec.data.tolist()
    indices = csr_vec.indices.tolist()
    indptr = csr_vec.indptr.tolist()
    shape = csr_vec.shape
    csr_dict = {'data':data,
                'indices': indices,
                'indptr':indptr,
                'shape':shape}
    return csr_dict

if __name__ == '__main__':

    # get all trail data from mongoDB
    client = pymongo.MongoClient("mongodb://user1:dva2020!@35.227.61.30/outdoor")
    db = client['outdoor']

    # Extract data from trail collection, each document is an item in a list
    print("Extracting trails from mongoDB...")
    start_time = time.time()
    trails = [doc for doc in db.trails.find({})]
    end_time = time.time()
    print("total time taken: ", end_time - start_time)

    # Create corpus, collect and store tokenized text for each trail, and also assess the difficulty
    corpus = []
    corpus_words = []
    print('Entering Loop to create corpus...')
    start_time = time.time()
    for idx, trail in enumerate(trails):
        trail['difficulty_map'] = map_difficulty(trail)
        all_text = join_all_text_field(trail)
        all_text = clean_text(all_text)
        text_list = tokenize_string(all_text)
        text_list = remove_stopwords(text_list)
        trail['tokenized_text'] = text_list # May not need, put here in case we want the full words
    #    text_list = lem_stem(text_list)
        corpus.append(' '.join(text_list))
        trail['index'] = idx
        for word in text_list:
            corpus_words.append(word)
    end_time = time.time()
    print("total time taken this loop: ", end_time - start_time)

    # Observe the distribution of words, for potential additions to stopwords
    fdist = FreqDist(corpus_words)

    # Train idf on corpus
    print("Training tfidf Vectorizer...")
    tfidf_vect, tfidf_matrix = tfidf(corpus)

    # Get feature names
    feature_array = np.array(tfidf_vect.get_feature_names())

    # Store the important keywords & full tfidf vectors for each trail
    print('Entering Loop to add tfidf vec to trail...')
    start_time = time.time()
    for idx,trail in enumerate(trails):
        csr_vec = tfidf_matrix[idx]
        trail['keywords'] = get_top_keywords(feature_array, csr_vec, n=10)
        trail['tfidf_vec'] = csr_todict(csr_vec)
    end_time = time.time()
    print("total time taken this loop: ", end_time - start_time)

    # Save the pre-trained tfidf model and sparse matrix
    print("Outputting tfidf vectorizer and doc matrix... ")
    pickle.dump(tfidf_vect, open("tfidf_model.sav", 'wb'))
    sparse.save_npz('sparse_matrix.npz', tfidf_matrix)

    #########################################################################################
    # THE BELOW METHODS MODIFY THE MONGODB COLLECTION, DO NOT UNCOMMENT UNLESS NECESSARY
    #########################################################################################
    # Method 1
    #########################################################################################
    # # Update the collection with new values - takes about 40mins (on a 16gb i7 machine)
    # print("Updating info on 'trails' MongoDB collection...")
    # for idx, trail in enumerate(trails):
    #     result = db.trails.update_one(
    #         {"_id": trail['_id']},
    #         {"$set":
    #              {"difficulty_map": trail['difficulty_map'],
    #               "tokenized_text": trail['tokenized_text'],
    #               "index": trail['index'],
    #               "keywords": trail['keywords'],
    #               "tfidf_vec": trail['tfidf_vec']}
    #          }
    #     )
    #     print(f"{idx} acknowledged: {result.acknowledged}")

    #########################################################################################
    # Method 2
    #########################################################################################
    ## Drop the collection and just re-upload it
    #db.trails.drop()
    #trails_collection = db['trails']
    #
    ## Insert the data into the trails collection
    #trails_collection.insert_many(trails)
    #print("Done, uploaded!")
