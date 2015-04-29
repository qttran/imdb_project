import os
# -*- coding: utf-8 -*-
db = DAL('sqlite://storage.sqlite')

db.define_table('top_actors',Field('actor_name'))
db.define_table('directors',Field('director_name'))

csv_data_folder = os.getcwd() + "/applications/imdb_project/csv_data/"
top_actors_file = csv_data_folder + "top_actors.csv"
directors_file = csv_data_folder + "directors.csv"

if db(db.top_actors).count() == 0:
    db.top_actors.import_from_csv_file(open(top_actors_file))
if db(db.directors.director_name.like("%")).count() == 0:
    db.directors.import_from_csv_file(open(directors_file))

#db.top_actors.widget = SQLFORM.widgets.autocomplete(request, db.category.name, limitby=(0,10), min_length=2)
