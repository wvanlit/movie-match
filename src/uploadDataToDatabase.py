from neo4j import GraphDatabase
import pandas
import credentials

driver = GraphDatabase.driver(credentials.neo4j_url, auth=(credentials.neo4j_user, credentials.neo4j_password))

def print_friends(tx):
    for record in tx.run("MATCH (m:Movie) RETURN m"):
        print(record['m']['title'])

def add_movie(tx, movie):
    tx.run("CREATE (m:Movie {movie_id:$id, title:$title, year:$year})", 
        id=movie['id'], title=movie['title'], year=movie['year'])

def add_user(tx, uid):
    tx.run("CREATE (u:User {user_id:$uid})", uid=uid)

def add_relation(tx, uid, movie_id, rating):
    tx.run("MATCH (u:User),(m:Movie) WHERE u.user_id = $uid AND m.movie_id = $mid CREATE ((u)-[r:rated { rating:$rating }]->(m))", 
            uid=uid, mid=movie_id, rating=rating)

csv = pandas.read_csv('../data/ml-latest-small/movies.csv')

with driver.session() as session:
    for index, row in csv.iterrows():
        # Clean Data
        fullTitle = row['title'].split('(')
        title = fullTitle[0].strip()
        if len(fullTitle) >= 2:
            year = fullTitle[len(fullTitle)-1].replace(')','').split('-')[0].strip()
        else:
            year = 0

        movie = {'id':row['movieId'], 'title':title, 'year':year}
        # Upload Node
        session.write_transaction(add_movie, movie)

        if index % 1000 == 0:
            print("Uploaded:",index,"movies")

csv = pandas.read_csv('../data/ml-latest-small/ratings.csv')
users = csv['userId'].unique()
with driver.session() as session:
    for user in users:
        session.write_transaction(add_user, int(user))

with driver.session() as session:
    for index, row in csv.iterrows():
        session.write_transaction(add_relation, row['userId'], row['movieId'], int(row['rating']))
        if index % 100 == 0:
            print("Uploaded:",index,"ratings")

driver.close()