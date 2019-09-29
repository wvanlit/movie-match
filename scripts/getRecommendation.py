from neo4j import GraphDatabase
import credentials
driver = GraphDatabase.driver(credentials.neo4j_url, auth=(credentials.neo4j_user, credentials.neo4j_password))

def getRecommendation(tx, uid):
	movies = []
	for movie in tx.run(""" MATCH (u1:User { user_id: $uid })-[r:rated]->(m:Movie)
							WITH u1, avg(r.rating) AS u1_mean

							MATCH (u1)-[r1:rated]->(m:Movie)<-[r2:rated]-(u2)
							WITH u1, u1_mean, u2, COLLECT({r1: r1, r2: r2}) AS ratings WHERE size(ratings) > 10

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
							ORDER BY score DESC LIMIT 10 """, uid=uid):
		movies.append(movie['m.title'])
	return movies


with driver.session() as session:
	print(session.write_transaction(getRecommendation, 42))



driver.close()