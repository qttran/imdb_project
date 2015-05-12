import sys
import csv
import numpy as np
from sklearn import linear_model
from sklearn import tree
from sklearn import ensemble
from sklearn.cross_validation import cross_val_score
np.set_printoptions(threshold = np.inf)

THRESHOLD_ACTORS = 11
THRESHOLD_DIRECTORS = 8
THRESHOLD_WRITERS = 11

def Read_Files(title):
	csv_file = csv.reader(open(title, 'r'))
	next(csv_file, None)

	return csv_file

# Preprocess movies_top_actors.csv, ignore uninformative data, and store the
# rest in a list.
def Movies_Top_Actors_Preprocessor(movies_top_actors):
	preprocessed_movies_top_actors = []
	for line in movies_top_actors:
		title, year = line[0], line[2]
		directors = line[4].split(';')
		top_actors = line[6].split(';')
		writers = line[8].split(';')
		rating, vote_count = line[9], line[10]
		genres = line[11].split(';')
		MPAA_rating, revenue, budget = line[12], line[13], line[14]

		if directors == [] or top_actors == [] or writers == [] or genres == [] \
		or revenue == '' or budget == '':
			continue
		elif float(revenue) < 1e+05 or float(budget) < 1e+05:
			continue
		else:
			preprocessed_movies_top_actors.append((title, int(year), directors, 
				top_actors, writers, float(rating), int(vote_count), genres, 
				MPAA_rating, float(revenue), float(budget)))
	return preprocessed_movies_top_actors

# Pick out actors shown up in more than 11 movies. There are 182 of them.
def Top_Actors_Preprocessor(preprocessed_movies_top_actors):
	preprocessed_top_actors = {}
	top_actors_statistics = {}
	for line in preprocessed_movies_top_actors:
		top_actors = line[3]
		rating, vote_count, revenue = line[5], line[6], line[9]

		for top_actor in top_actors:
			if top_actor not in top_actors_statistics:
				top_actors_statistics[top_actor] = \
				[((rating, vote_count), revenue)]
			else:
				top_actors_statistics[top_actor].append\
				(((rating, vote_count), revenue))
		for top_actor in top_actors_statistics:
			if len(top_actors_statistics[top_actor]) >= THRESHOLD_ACTORS:
				preprocessed_top_actors[top_actor] = \
				top_actors_statistics[top_actor]

	return preprocessed_top_actors

# Pick out directors direct more than 8 movies. There are 49 of them.
def Directors_Preprocessor(preprocessed_movies_top_actors):
	preprocessed_directors = {}
	directors_statistics = {}
	for line in preprocessed_movies_top_actors:
		directors = line[2]
		rating, vote_count, revenue = line[5], line[6], line[9]

		for director in directors:
			if director not in directors_statistics:
				directors_statistics[director] = \
				[((rating, vote_count), revenue)]
			else:
				directors_statistics[director].append\
				(((rating, vote_count), revenue))
		for director in directors_statistics:
			if len(directors_statistics[director]) >= THRESHOLD_DIRECTORS:
				preprocessed_directors[director] = \
				directors_statistics[director]

	return preprocessed_directors

# Pick out writers write more than 11 movies. There are 43 of them.
def Writers_Preprocessor(preprocessed_movies_top_actors):
	preprocessed_writers = {}
	writers_statistics = {}
	for line in preprocessed_movies_top_actors:
		writers = line[4]
		rating, vote_count, revenue = line[5], line[6], line[9]

		for writer in writers:
			if writer not in writers_statistics:
				writers_statistics[writer] = \
				[((rating, vote_count), revenue)]
			else:
				writers_statistics[writer].append\
				(((rating, vote_count), revenue))
		for writer in writers_statistics:
			if len(writers_statistics[writer]) >= THRESHOLD_WRITERS:
				preprocessed_writers[writer] = \
				writers_statistics[writer]

	return preprocessed_writers

# Without the uninformative data, there are 21 genres left.
def Genres_Preprocessor(preprocessed_movies_top_actors):
	preprocessed_generes = set()
	for line in preprocessed_movies_top_actors:
		genres = line[7]
		for genre in genres:
			preprocessed_generes.add(genre)

	return preprocessed_generes 

# Build a dictionary for feature extractor/
def Feature_Preprocessor(preprocessed_top_actors, preprocessed_directors, 
	preprocessed_writers, preprocessed_generes):
	preprocessed_features = {'top_actors':{}, 'directors':{}, 'writers':{}, 'genres':{},\
	 'MPAA_ratings':{'':1, 'PG':2, 'PG-13':3, 'R':4, 'NC-17':5}}
	last_feature_id = 4
	for top_actor in preprocessed_top_actors:
		last_feature_id += 1
		preprocessed_features['top_actors'][top_actor] = last_feature_id
	for director in preprocessed_directors:
		last_feature_id += 1
		preprocessed_features['directors'][director] = last_feature_id
	for writer in preprocessed_writers:
		last_feature_id += 1
		preprocessed_features['writers'][writer] = last_feature_id
	for genre in preprocessed_generes:
		last_feature_id += 1
		preprocessed_features['genres'][genre] = last_feature_id

	return preprocessed_features, last_feature_id

# Feature ectracting for the whole training data set.
def Movies_Feature_Extractor(preprocessed_features, last_feature_id, 
	preprocessed_movies_top_actors):
	inputs = np.zeros((3000, last_feature_id + 1))
	outputs_rating, outputs_revenue = np.zeros(3000), np.zeros(3000)
	effective_training_data = 0
	for line in preprocessed_movies_top_actors:
		inputs[effective_training_data, :], outputs_rating[effective_training_data],\
		 outputs_revenue[effective_training_data] = Feature_Extractor(line, 
		 	last_feature_id, preprocessed_features)
		effective_training_data += 1

	inputs = inputs[0:effective_training_data, :]
	outputs_rating = outputs_rating[0:effective_training_data]
	outputs_revenue = outputs_revenue[0:effective_training_data]

	return inputs, outputs_rating, outputs_revenue

# Feature extracting for a single training data.
def Feature_Extractor(line, last_feature_id, preprocessed_features):
	directors = line[2]
	top_actors = line[3]
	writers = line[4]
	genres = line[7]
	MPAA_rating = line[8]
	rating, vote_count = line[5], line[6]
	revenue, budget = line[9], line[10]
		
	inputs = np.zeros(last_feature_id + 1)	
	output_rating = rating
	output_revenue = revenue
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

	return inputs, output_rating, output_revenue

# Try out 4 different regression models: RidgeCV, LassoCV, LinearRegression, DecisionTreeRegressor
def Regression_Models(inputs, outputs_rating, outputs_revenue, preprocessed_features, 
	last_feature_id, preprocessed_movies_top_actors):
	
	clf_rating_ridge = linear_model.RidgeCV(alphas = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0], normalize = True)
	clf_rating_ridge.fit(inputs, outputs_rating)
	#print 'The R-square of prediction is', clf_rating_ridge.score(inputs, outputs_rating)
	#print clf_rating_ridge.alpha_, clf_rating_ridge.coef_

	clf_revenue_ridge = linear_model.RidgeCV(alphas = [1e+05, 1e+06, 1e+07, 1e+08, 1e+09])
	clf_revenue_ridge.fit(inputs, outputs_revenue)
	#print 'The R-square of prediction is', clf_revenue_ridge.score(inputs, outputs_revenue)
	#print clf_revenue_ridge.alpha_, clf_revenue_ridge.coef_

	clf_rating_lasso = linear_model.LassoCV(alphas = [0.01, 0.1, 1.0, 10.0, 100.0], normalize = True)
	clf_rating_lasso.fit(inputs, outputs_rating)
	#print 'The R-square of prediction is', clf_rating_lasso.score(inputs, outputs_rating)
	#print clf_rating_lasso.alpha_, clf_rating_lasso.coef_ 

	clf_revenue_lasso = linear_model.LassoCV(alphas = [1e+03, 1e+04, 1e+05, 1e+06, 1e+07])
	clf_revenue_lasso.fit(inputs, outputs_revenue)
	#print 'The R-square of prediction is', clf_revenue_lasso.score(inputs, outputs_revenue)
	#print clf_revenue_lasso.alpha_, clf_revenue_lasso.coef_ 

	clf_rating_linearR = linear_model.LinearRegression(normalize = True)
	clf_rating_linearR.fit(inputs, outputs_rating)
	#print 'The R-square of predition is', clf_rating_linearR.score(inputs, outputs_rating)
	#print clf_rating_linearR.coef_

	clf_revenue_linearR = linear_model.LinearRegression(normalize = True)
	clf_revenue_linearR.fit(inputs, outputs_revenue)
	#print 'The R-square of predition is', clf_revenue_linearR.score(inputs, outputs_revenue)
	#print clf_revenue_linearR.coef_

	tree_rating = tree.DecisionTreeRegressor(max_depth = 10, random_state = 0)
	tree_rating.fit_transform(inputs, outputs_rating)
	#tree.export_graphviz(tree_rating, out_file = 'rating_decision_tree.dot')
	#print tree_rating.max_features_
	#print tree_rating.feature_importances_
	#print 'The 10-fold cross validations are', \
	#cross_val_score(tree_rating, inputs, outputs_rating, cv=10)

	tree_revenue = tree.DecisionTreeRegressor(max_depth = 10, random_state = 0)
	tree_revenue.fit_transform(inputs, outputs_revenue)
	#tree.export_graphviz(tree_revenue, out_file = 'revenue_decision_tree.dot')
	#print tree_revenue.max_features_
	#print tree_revenue.feature_importances_
	#print 'The 10-fold cross validations are', \
	#cross_val_score(tree_revenue, inputs, outputs_rating, cv=10)

	random_forest_rating_MD5 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 5, random_state = 0)
	random_forest_rating_MD5.fit_transform(inputs, outputs_rating)
	#print random_forest_rating_MD5.estimators_
	#print random_forest_rating_MD5.feature_importances_
	#print 'The 10-fold cross validations are', \
	#cross_val_score(random_forest_rating_MD5, inputs, outputs_rating, cv=10)


	random_forest_revenue_MD5 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 5, random_state = 0)
	random_forest_revenue_MD5.fit_transform(inputs, outputs_revenue)
	#print random_forest_revenue_MD5.estimators_
	#print random_forest_revenue_MD5.feature_importances_
	#print 'The 10-fold cross validations are', \
	#cross_val_score(random_forest_revenue_MD5, inputs, outputs_rating, cv=10)

	random_forest_rating_MD10 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 10, random_state = 0)
	random_forest_rating_MD10.fit_transform(inputs, outputs_rating)

	random_forest_revenue_MD10 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 10, random_state = 0)
	random_forest_revenue_MD10.fit_transform(inputs, outputs_revenue)
	
	random_forest_rating_MD15 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 15, random_state = 0)
	random_forest_rating_MD15.fit_transform(inputs, outputs_rating)

	random_forest_revenue_MD15 = ensemble.RandomForestRegressor(n_estimators = 10, 
		max_depth = 15, random_state = 0)
	random_forest_revenue_MD15.fit_transform(inputs, outputs_revenue)


	# Compare the prediction with training data set.
	for line in preprocessed_movies_top_actors:
		test_input, test_output_rating, test_output_revenue = Feature_Extractor(line, 
			last_feature_id, preprocessed_features)
		print 'The true rating is ', test_output_rating
		print 'The predicted rating cia clf_ridge is', clf_rating_ridge.predict(test_input)
		print 'The predicted rating cia clf_lasso is', clf_rating_lasso.predict(test_input)
		print 'The predicted rating cia clf_linearR is', clf_rating_linearR.predict(test_input)
		print 'The predicted rating via tree is', tree_rating.predict(test_input)
		print 'The predicted rating via random forest Max Depth = 5 is', random_forest_rating_MD5.predict(test_input)
		print 'The predicted rating via random forest Max Depth = 10 is', random_forest_rating_MD10.predict(test_input)
		print 'The predicted rating via random forest Max Depth = 15 is', random_forest_rating_MD15.predict(test_input)




		print 'The true revenue is', test_output_revenue
		print 'The predicted revenue via clf_ridge is', clf_revenue_ridge.predict(test_input)
		print 'The predicted revenue via clf_lasso is', clf_revenue_lasso.predict(test_input)
		print 'The predicted revenue via clf_linearR is', clf_revenue_linearR.predict(test_input)
		print 'The predicted revenue via tree is', tree_revenue.predict(test_input)
		print 'The predict revenue via random forest Max Depth = 5 is', random_forest_revenue_MD5.predict(test_input)
		print 'The predict revenue via random forest Max Depth = 10 is', random_forest_revenue_MD10.predict(test_input)
		print 'The predict revenue via random forest Max Depth = 15 is', random_forest_revenue_MD15.predict(test_input)
		
		#print '______________________________________'

if __name__ == '__main__':
	movies_top_actors = Read_Files(sys.argv[1]) 

	preprocessed_movies_top_actors = Movies_Top_Actors_Preprocessor(movies_top_actors)

	preprocessed_top_actors = Top_Actors_Preprocessor(preprocessed_movies_top_actors)
	preprocessed_directors = Directors_Preprocessor(preprocessed_movies_top_actors)
	preprocessed_writers = Writers_Preprocessor(preprocessed_movies_top_actors)
	preprocessed_generes = Genres_Preprocessor(preprocessed_movies_top_actors)

	preprocessed_features, last_feature_id = Feature_Preprocessor(preprocessed_top_actors,
	 preprocessed_directors, preprocessed_writers, preprocessed_generes)

	inputs, outputs_rating, outputs_revenue = Movies_Feature_Extractor(preprocessed_features,\
	 last_feature_id, preprocessed_movies_top_actors)

	Regression_Models(inputs, outputs_rating, outputs_revenue, preprocessed_features,\
	 last_feature_id, preprocessed_movies_top_actors)

	
