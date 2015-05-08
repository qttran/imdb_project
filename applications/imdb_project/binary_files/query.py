import sys
import csv
import string
import operator
import cPickle as pickle

# arguments:
#		- movies_file: the filename of the full movies dataset
#		- directors_file: the filename of the directors inverted index
#		- actors_file: the filename of the actors inverted index
#		- genres_file: the filename of the genres inverted index
#		- mpaa_file: the filename of the MPAA rating inverted index
#		- directors: a list of strings of the directors being queried, [] if no directors specified
#		- actors: a list of strings of the actors being queried, [] if no actors specified
#		- genres: a list of strings of the genres being queried, [] if no genre specified
#		- mpaa: a string of the MPAA rating being queried, "" if no MPAA rating specified
def query(movies_file, directors_file, actors_file, genres_file, mpaa_file, directors, actors, genres, mpaa):
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
	
	for i in range(0,5):
		if similar_movies != {}:
			most_similar = max(similar_movies.iteritems(), key=operator.itemgetter(1))
			print most_similar
			del similar_movies[most_similar[0]]


def main():
	query("movies_top_actors.csv", "directors_invIndex.p", "actors_invIndex.p", "genres_invIndex.p", "mpaa_invIndex.p",
		["Quentin Tarantino", "Steven Spielberg"], ["Emma Watson", "Anne Hathaway"], ["Comedy", "Romance"], "PG-13")

if __name__ == '__main__':
	main()