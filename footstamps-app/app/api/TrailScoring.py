import pickle
from scipy.stats import norm
from scipy.sparse import load_npz, vstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TrailScorer:
    def __init__(self, path_to_tfidf_vect, path_to_doc_matrix, user_dict):
        self.tfidf_vectorizer = pickle.load(open(path_to_tfidf_vect, 'rb'))
        self.doc_matrix = load_npz(path_to_doc_matrix)
        self.wl = 0.35
        self.wd = 0.35
        self.wq = 0.3
        self.user_length= user_dict['length']
        self.user_difficulty = user_dict['difficulty']
        self.user_query = user_dict['query']
        self.co_sim_vec = self._co_sim_vec()

    def _co_sim_vec(self):
        '''Returns a single vector representing the similarity of users inputs to all trails'''
        # Transform user inputs to tfidf representation based on trained corpus data
        user_vec = [self.user_query]
        user_tfidf_vec = self.tfidf_vectorizer.transform(user_vec)

        # Find cosine sim across all rows of doc matrix compared to user vec
        co_sim_vec= cosine_similarity(self.doc_matrix, user_tfidf_vec) # Vector w/ shape (79127, 1), in csr format

        return co_sim_vec

    def _query_score(self,trail_row_num):
        '''Returns weighted user query score'''
        # Extract the cosine sim score from the vector
        co_sim = self.co_sim_vec[trail_row_num].item()

        # Handmade polynomial so that our similarity score mapping is a little more human
        co_sim_trfm = -2.7975*co_sim**4 + 6.817*co_sim**3 - 6.5364*co_sim**2 + 3.3984*co_sim + 0.1084

        sq = co_sim_trfm*100

        return self.wq*sq

    def _length_score(self, trail_length, sigma=0.5):
        '''Returns weighted trail length score'''
        max_pdf = norm.pdf(trail_length, loc=trail_length, scale=sigma)
        pdf = norm.pdf(self.user_length, loc=trail_length, scale=sigma)
        sl = (pdf/max_pdf)*100
        return self.wl*sl

    def _diff_score(self, trail_difficulty):
        '''Returns weighted trail difficulty score'''
        dmap = {'Easy': 0, 'Intermediate': 1, 'Difficult': 2}
        smap = {0: 100,
                1: 50,
                2: 0}
        difference = dmap.get(trail_difficulty, 1) - dmap.get(self.user_difficulty, 1)
        sd = smap[abs(difference)]
        return self.wd*sd

    def score_one(self, trail_dict):
        '''Returns total trail score '''
        trail_length = trail_dict['length_mi']
        trail_difficulty = trail_dict['difficulty_map']
        trail_row_num = trail_dict['index']

        wsl = self._length_score(trail_length)
        wsd = self._diff_score(trail_difficulty)
        wsq = self._query_score(trail_row_num)

        return round(wsl + wsd + wsq)

    def score_many(self, trails_list):
        '''Returns a dict of all trails and their recommendation score'''
        scored_trails = {}
        for trail_dict in trails_list:
            trail_id = trail_dict['_id']
            score = self.score_one(trail_dict)
            scored_trails[trail_id] = score
        return scored_trails