from flask import Flask
from flask import request, abort, jsonify
from neo4j import GraphDatabase
import credentials

app = Flask(__name__)
driver = GraphDatabase.driver(credentials.neo4j_url, auth=(credentials.neo4j_user, credentials.neo4j_password))

def create_user(tx, uid, uname):
    tx.run("CREATE (u:User {user_id:$uid, username:$uname})", uid=uid, uname=uname)

def create_relation(tx, uname, mtitle, rating):
    tx.run("MATCH (u:User),(m:Movie) WHERE u.username = $uname AND m.title = $mtitle CREATE ((u)-[r:rated { rating:$rating }]->(m))", 
            uname=uname, mtitle=mtitle, rating=rating)

def has_relation(tx, uname, mtitle):
	outcome = tx.run("MATCH (u:User)-[r:rated]->(m:Movie) WHERE u.username = $uname and m.title = $mtitle RETURN m", 
            uname=uname, mtitle=mtitle)
	return outcome.single() != None

def recommendMovie(tx, movietitle):
	movies = ''
	for movie in tx.run('''
		MATCH (m:Movie {title: $movietitle})<-[r1:rated]-(:User)-[r2:rated]->(o:Movie) 
		WHERE r1.rating = 5 
		RETURN o.title as Title, AVG(r2.rating) as Rating, COUNT(r2)*AVG(r2.rating) as Score ORDER BY Score DESC LIMIT 10''', 
		movietitle = movietitle):
		movies += movie['Title']+';'
	return movies[:-1]

def recommendUser(tx, uname):
	movies = ''
	for movie in tx.run(""" MATCH (u1:User { username: $uname })-[r:rated]->(m:Movie)
							WITH u1, avg(r.rating) AS u1_mean

							MATCH (u1)-[r1:rated]->(m:Movie)<-[r2:rated]-(u2)
							WITH u1, u1_mean, u2, COLLECT({r1: r1, r2: r2}) AS ratings WHERE size(ratings) > 3

							MATCH (u2)-[r:rated]->(m:Movie)
							WITH u1, u1_mean, u2, avg(r.rating) AS u2_mean, ratings

							UNWIND ratings AS r

							WITH sum( (r.r1.rating-u1_mean) * (r.r2.rating-u2_mean) ) AS nom,
							     sqrt( sum( (r.r1.rating - u1_mean)^2) * sum( (r.r2.rating - u2_mean) ^2)) AS denom,
							     u1, u2 WHERE denom <> 0

							WITH u1, u2, nom/denom AS pearson
							ORDER BY pearson DESC LIMIT 5

							MATCH (u2)-[r:rated]->(m:Movie) WHERE NOT EXISTS( (u1)-[:rated]->(m) )

							RETURN m.title, SUM( pearson * r.rating) AS score
							ORDER BY score DESC LIMIT 10 """, uname=uname):
		movies += movie['m.title']+';'
	return movies[:-1]

def getHighestUserID(tx):
	for user_id in tx.run("MATCH (u:User) RETURN u.user_id ORDER BY u.user_id DESC LIMIT 1"):
		return user_id[0]

def checkIfUserIdExists(tx, uid):
	result = tx.run("MATCH (u:User) WHERE u.user_id = $uid RETURN u.user_id ORDER BY u.user_id DESC LIMIT 1", uid=uid)
	if result.single() is None:
		return False
	else:
		return True

def checkIfUserNameExists(tx, uname):
	result = tx.run("MATCH (u:User) WHERE u.username = $uname RETURN u.user_id ORDER BY u.user_id DESC LIMIT 1", uname=uname)
	if result.single() is None:
		return False
	else:
		return True

@app.route('/movie-match/recommendUser/<username>', methods=['GET'])
def get_user_recommendation(username):
	with driver.session() as session:
		return session.write_transaction(recommendUser, username), 201

@app.route('/movie-match/recommendMovie/<movie>', methods=['GET'])
def get_movie_recommendation(movie):
	with driver.session() as session:
		return session.write_transaction(recommendMovie, movie), 201

# JSON : {"username":"", "title":"", rating:"":0}
@app.route('/movie-match/addRelation', methods=['POST'])
def add_relation():
	if not request.json:
		abort(400)
	if not 'username' in request.json or not 'title' in request.json or not 'rating' in request.json:
		abort(400)

	with driver.session() as session:
		# Check if relation already exists
		if session.write_transaction(has_relation, request.json['username'], request.json['title']):
			return jsonify({'error':'Relation Already Exist'}), 200

		# Create new relation
		session.write_transaction(create_relation, request.json['username'], request.json['title'], request.json['rating'])
	return jsonify(request.json),201




# JSON : {"name", "movies":[{"title":"", "rating":0}]}
@app.route('/movie-match/addUser', methods=['POST'])
def add_user():
	if not request.json or not 'name' in request.json:
		abort(400)

	with driver.session() as session:
		userExists = session.write_transaction(checkIfUserNameExists, request.json['name'])
		uid = session.write_transaction(getHighestUserID)+1

		if userExists:
			return jsonify({'error':'User Already Exist'}), 200

		if not 'movies' in request.json:
			request.json['movies'] = []

		# Create User
		session.write_transaction(create_user, uid, request.json['name'])

		# Add Movie Relations
		for movie in request.json['movies']:
			if not 'title' in movie and not 'rating' in movie:
				return jsonify({'error':'No title or rating in movie'}), 200
			session.write_transaction(create_relation, request.json['name'], movie['title'], movie['rating'])

	user = {
	'id': uid,
	'name': request.json['name'],
	'movies': request.json['movies'],
	}
	return jsonify({'user': user}), 201


if __name__ == '__main__':
	app.run(debug=False)
	driver.close()
