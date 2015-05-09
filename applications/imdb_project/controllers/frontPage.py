# -*- coding: utf-8 -*-
# try something like
import sys
import csv
import string
import operator
import cPickle as pickle
import os
import json
import numpy as np
from sklearn import linear_model
from sklearn import tree
from sklearn import ensemble
from sklearn.cross_validation import cross_val_score
np.set_printoptions(threshold = np.inf)

MAX_RETURN_NUM = 3
binary_file_folder = os.getcwd() + "/applications/imdb_project/binary_files/"

def index():
    return dict()

def getRatingAndRevenue():
    csvInput= request.vars.values()[0]
    output = "keke"

    last_feature_id = 294
    clf_revenue_file = binary_file_folder + "clf_revenue.p"
    clf_rating_file = binary_file_folder + "clf_rating.p"
    random_forest_revenue_file = binary_file_folder + "random_forest_revenue.p"
    random_forest_rating_file = binary_file_folder + "random_forest_rating.p"
    preprocessed_features_file = binary_file_folder + "preprocessed_features.p"

    clf_revenue = pickle.load(open(clf_revenue_file, "rb"))
    clf_rating = pickle.load(open(clf_rating_file, "rb"))
    #random_forest_revenue = pickle.load(open(random_forest_revenue_file, "rb"))
    #random_forest_rating = pickle.load(open(random_forest_rating_file, "rb"))
    preprocessed_features = pickle.load(open(preprocessed_features_file, "rb"))

    processed_input = preprocess_movie_input(csvInput)
    if len(processed_input) == 0:
        return "INPUT ERR, INPUT ERR"
    ml_input = Feature_Extractor(processed_input, last_feature_id, preprocessed_features)
    predicted_revenue = clf_revenue.predict(ml_input)
    predicted_rating = clf_rating.predict(ml_input)
    return str(predicted_rating) + "," + str(predicted_revenue)

def movieSuggestions():
    actors= request.vars.values()[3].split(", ")
    directors= request.vars.values()[1].split(", ")
    writers = request.vars.values()[2].split(", ")
    genres= request.vars.values()[4].split(", ")
    mpaa= request.vars.values()[0]
    
    directors_file = binary_file_folder + "directors_invIndex.p"
    actors_file = binary_file_folder + "actors_invIndex.p"
    genres_file = binary_file_folder + "genres_invIndex.p"
    mpaa_file = binary_file_folder + "mpaa_invIndex.p"
    rating_hashmap_file = binary_file_folder + "ratings_hashmap.p"
    movie_title_name_hashmap_file = binary_file_folder + "movie_title_name_hashMap.p"
    d_index = pickle.load(open(directors_file, "rb"))
    a_index = pickle.load(open(actors_file, "rb"))
    g_index = pickle.load(open(genres_file, "rb"))
    m_index = pickle.load(open(mpaa_file, "rb"))
    ratings_hashmap = pickle.load(open(rating_hashmap_file, "rb"))
    movie_title_name = pickle.load(open(movie_title_name_hashmap_file, "rb"))
    similar_movies = {}
    # for each queried director, add 1 to the similarity score of any movie with that director
    for d in directors:
        if d not in d_index:
            continue
        for movie in d_index[d]:
			if movie in similar_movies:
				similar_movies[movie] += 1
			else:
				similar_movies[movie] = 1

	# for each queried actor, add 1 to the similarity score of any movie with that actor
    for a in actors:
        if a not in a_index:
            continue
        for movie in a_index[a]:
            if movie in similar_movies:
                similar_movies[movie] += 1.5
            else:
                similar_movies[movie] = 1.5

    # add 1 to the similarity score of any movie with the queried genre
    for g in genres:
        if g not in g_index:
            continue
        for movie in g_index[g]:
            if movie in similar_movies:
                similar_movies[movie] += 1.5
            else:
                similar_movies[movie] = 1.5
    # add 1 to the similarity score of any movie with the queried MPAA rating
    if mpaa != "":
        if mpaa in m_index:
            for movie in m_index[mpaa]:
                if movie in similar_movies:
                    similar_movies[movie] += 1
                else:
                    similar_movies[movie] = 1

    for key in similar_movies:
        rating = ratings_hashmap[key]
        if rating == "":
            num_rating = 0
        else:
            num_rating = float(rating)
        similar_movies[key] = similar_movies[key]*1000 + num_rating

    most_similars = ""
    for i in range(0,6):
        if similar_movies != {}:
            most_similar = max(similar_movies.iteritems(), key=operator.itemgetter(1))
        else:
            break
        most_similars += most_similar[0] + ","
        most_similars += movie_title_name[most_similar[0]] + ","
        del similar_movies[most_similar[0]]

    return most_similars



def movieLiveSearch():
    partialstr = request.vars.values()[0]
    
    query = db.movies.title.like(partialstr+'%') # Query for first name
    results = db(query).select(db.movies.ALL, limitby = (0,MAX_RETURN_NUM))
    suggested_movies = [row for row in results]
    
    movie_infos = []
    
    titles = []
    for i, suggested_movie in enumerate(suggested_movies): # Return
        if (suggested_movie not in titles):
            titles.append(suggested_movie)
    return DIV(*[DIV(k.title,
                     _onclick="""jQuery('#movies').val('%s'); 
                                 jQuery('#actors').val('%s');
                                 jQuery('#directors').val('%s');
                                 jQuery('#writers').val('%s');
                                 hide()"""
                                 % (k.title,
                                    k.cast_names.replace(";", ", "),
                                    k.director_names.replace(";", ", "),
                                    k.writer_names.replace(";", ", ")),
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in titles])

def actorLiveSearch():
    partialstr = request.vars.values()[0]
    already_searched = ""
    if ',' in partialstr:
        list_of_actors = partialstr.rsplit(',',1)
        already_searched = list_of_actors[0] + ", "
        partialstr = list_of_actors[1].strip()

    query = db.top_actors.actor_name.like(partialstr+'%') # Query for first name
    results = db(query).select(db.top_actors.ALL, limitby = (0,MAX_RETURN_NUM))
    suggested_actors = [row.actor_name for row in results]
    items = []

    first_name_suggestions_num = len(results) # If query for first name doesn't give enough results, query for last name
    if first_name_suggestions_num < MAX_RETURN_NUM:
        query = db.top_actors.actor_name.like('% ' + partialstr+'%')
        results = db(query).select(db.top_actors.ALL, limitby = (0,MAX_RETURN_NUM - first_name_suggestions_num))
        for row in results:
            suggested_actors.append(row.actor_name)

    for i, suggested_actor in enumerate(suggested_actors): # Return
        if (suggested_actor not in items):
            items.append(suggested_actor)
    return DIV(*[DIV(k,
                     _onclick="jQuery('#actors').val('%s'); hide()" % (already_searched + k + ', ') ,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])


def directorLiveSearch():
    #TODO search engine
    partialstr = request.vars.values()[0]
    already_searched = ""
    if ',' in partialstr:
        list_of_directors = partialstr.rsplit(',',1)
        already_searched = list_of_directors[0] + ", "
        partialstr = list_of_directors[1].strip()
    query = db.directors.director_name.like(partialstr+'%') # Query for first name
    results = db(query).select(db.directors.ALL, limitby = (0,MAX_RETURN_NUM))
    suggested_directors = [row.director_name for row in results]
    items = []

    first_name_suggestions_num = len(results) # If query for first name doesn't give enough results, query for last name
    if first_name_suggestions_num < MAX_RETURN_NUM:
        query = db.directors.director_name.like('% ' + partialstr+'%') 
        results = db(query).select(db.directors.ALL, limitby = (0,MAX_RETURN_NUM - first_name_suggestions_num))
        for row in results:
            suggested_directors.append(row.director_name)

    for i, suggested_director in enumerate(suggested_directors): # Return
        if (suggested_director not in items):
            items.append(suggested_director)

    return DIV(*[DIV(k,
                     _onclick="jQuery('#directors').val('%s'); hide()" % (already_searched + k + ', ') ,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])


def writerLiveSearch():
    partialstr = request.vars.values()[0]
    already_searched = ""
    if ',' in partialstr:
        list_of_writers = partialstr.rsplit(',',1)
        already_searched = list_of_writers[0] + ", "
        partialstr = list_of_writers[1].strip()
    query = db.writers.writer_name.like(partialstr+'%') # Query for first name
    results = db(query).select(db.writers.ALL, limitby = (0,MAX_RETURN_NUM))
    suggested_writers = [row.writer_name for row in results]
    items = []

    first_name_suggestions_num = len(results) # If query for first name doesn't give enough results, query for last name
    if first_name_suggestions_num < MAX_RETURN_NUM:
        query = db.writers.writer_name.like('% ' + partialstr+'%')
        results = db(query).select(db.writers.ALL, limitby = (0,MAX_RETURN_NUM - first_name_suggestions_num))
        for row in results:
            suggested_writers.append(row.writer_name)

    for i, suggested_writer in enumerate(suggested_writers): # Return
        if (suggested_writer not in items):
            items.append(suggested_writer)

    return DIV(*[DIV(k,
                     _onclick="jQuery('#writers').val('%s'); hide()" % (already_searched + k + ', '),
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])

#helper method for ML
def Feature_Extractor(line, last_feature_id, preprocessed_features):
	directors = line[2]
	top_actors = line[3]
	writers = line[4]
	genres = line[7]
	MPAA_rating = line[8]
	revenue, budget = line[9], line[10]

	inputs = np.zeros(last_feature_id + 1)
	inputs[0] = budget
	inputs[1] = len(top_actors)
	inputs[2] = len(directors)
	inputs[3] = len(writers)
	inputs[4] = preprocessed_features['MPAA_ratings'][MPAA_rating]
	for top_actor in top_actors:
		if top_actor in preprocessed_features['top_actors']:
			feature_id = preprocessed_features['top_actors'][top_actor]
			inputs[feature_id] = 1.0
	for director in directors:
		if director in preprocessed_features['directors']:
			feature_id = preprocessed_features['directors'][director]
			inputs[feature_id] = 1.0
	for writer in writers:
		if writer in preprocessed_features['writers']:
			feature_id = preprocessed_features['writers'][writer]
			inputs[feature_id] = 1.0
	for genre in genres:
		feature_id = preprocessed_features['genres'][genre]
		inputs[feature_id] = 1.0

	return inputs

def preprocess_movie_input(csvLine):
    line = csvLine.split(',')
    preprocessed_movies_top_actors = []
    title, year = line[0], line[2]
    directors = line[4].split(';')
    top_actors = line[6].split(';')
    writers = line[8].split(';')
    rating, vote_count = line[9], line[10]
    genres = line[11].split(';')
    MPAA_rating, revenue, budget = line[12], line[13], line[14]
    if (MPAA_rating == "G"):
        MPAA_rating = ""

    if directors == [] or top_actors == [] or writers == [] or genres == [] or revenue == '' or budget == '':
        return []
    else:
        preprocessed_movies_top_actors = (title, year, directors,
            top_actors, writers, rating, vote_count, genres,
            MPAA_rating, revenue, budget)
    return preprocessed_movies_top_actors
