# -*- coding: utf-8 -*-
# try something like
import sys
import csv
import string
import operator
import cPickle as pickle
import os

MAX_RETURN_NUM = 3

def index():
    return dict()

def movieSuggestions():
    actors= request.vars.values()[3].split(", ")
    directors= request.vars.values()[1].split(", ")
    writers = request.vars.values()[2].split(", ")
    genres= request.vars.values()[4].split(", ")
    mpaa= request.vars.values()[0]
    
    binary_file_folder = os.getcwd() + "/applications/imdb_project/binary_files/"
    directors_file = binary_file_folder + "directors_invIndex.p"
    actors_file = binary_file_folder + "actors_invIndex.p"
    genres_file = binary_file_folder + "genres_invIndex.p"
    mpaa_file = binary_file_folder + "mpaa_invIndex.p"
    d_index = pickle.load(open(directors_file, "rb"))
    a_index = pickle.load(open(actors_file, "rb"))
    g_index = pickle.load(open(genres_file, "rb"))
    m_index = pickle.load(open(mpaa_file, "rb"))
    similar_movies = {}
    # for each queried director, add 1 to the similarity score of any movie with that director
    for d in directors:
		for movie in d_index[d]:
			if movie in similar_movies:
				similar_movies[movie] += 1
			else:
				similar_movies[movie] = 1

	# for each queried actor, add 1 to the similarity score of any movie with that actor
    for a in actors:
        for movie in a_index[a]:
            if movie in similar_movies:
                similar_movies[movie] += 1
            else:
                similar_movies[movie] = 1

    # add 1 to the similarity score of any movie with the queried genre
    for g in genres:
        for movie in g_index[g]:
            if movie in similar_movies:
                similar_movies[movie] += 1
            else:
                similar_movies[movie] = 1
    # add 1 to the similarity score of any movie with the queried MPAA rating
    if mpaa != "":
        for movie in m_index[mpaa]:
            if movie in similar_movies:
                similar_movies[movie] += 1
            else:
                similar_movies[movie] = 1

    most_similars = []
    for i in range(0,5):
        if similar_movies != {}:
            most_similar = max(similar_movies.iteritems(), key=operator.itemgetter(1))
        most_similars.append(most_similar)
        del similar_movies[most_similar[0]]
        
    return DIV(*[DIV(most_similars[0])])

    

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
                     _onclick="jQuery('#directors').val('%s'); hide()" % (already_searched + k + ', '),
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])
