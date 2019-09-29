from neo4j import GraphDatabase
import credentials

def getTopNMovies(tx, n):
	result = tx.run("MATCH (m:Movie)<-[r:rated]-(:User) RETURN m.title as Title, COUNT(r) as Reviews ORDER BY Reviews DESC LIMIT $n", n=n)
	return [record["Title"] for record in result]
# Get Movies
driver = GraphDatabase.driver(credentials.neo4j_url, auth=(credentials.neo4j_user, credentials.neo4j_password))

with driver.session() as session:
		movieList = session.write_transaction(getTopNMovies, 5000)
driver.close()
# Iterate over list and put titles in a string
index = 0
movieString = 'var movieList = ['
for movie in movieList:
	movieString += f'"{movie}",'
	index += 1
	if index >= 5000:
		break
movieString += ']'

# Create file
target = open('../web/js/movieList.js', 'w')

target.write(movieString)



