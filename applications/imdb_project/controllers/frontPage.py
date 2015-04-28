# -*- coding: utf-8 -*-
# try something like
def index(): 
    return dict()

def actorLiveSearch():
    #TODO search engine
    partialstr = request.vars.values()[0]
    items = []
    if partialstr == "b":
        items.append("Brad Pitt")
    items.append("other actors")
    
    return DIV(*[DIV(k,
                     #_onclick="jQuery('#month').val('%s')" % k,
                     _onclick="jQuery('#actors').val('%s'); hide()" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])


def directorLiveSearch():
    #TODO search engine
    partialstr = request.vars.values()[0]
    items = []
    items.append("Director 1")
    items.append("director 2")
    
    return DIV(*[DIV(k,
                     #_onclick="jQuery('#month').val('%s')" % k,
                     _onclick="jQuery('#directors').val('%s'); hide()" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'",
                     _id="resultLiveSearch"
                     ) for k in items])
                     
#    partialstr = request.vars.values()[0]
#    query = db.actor.name.like('%'+partialstr+'%')
#    countries = db(query).select(db.actor.name)
#    items = []
#for (i,actor) in enumerate(actors):
#       items.append(DIV(A(actor.name, _id="res%s"%i, _href="#", _onclick="copyToBox($('#res%s').html())"%i), _id="resultLiveSearch"))
#    return TAG[''](*items) -->
