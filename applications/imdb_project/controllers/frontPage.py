# -*- coding: utf-8 -*-
# try something like
MAX_RETURN_NUM = 3

def index():
    return dict()

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
