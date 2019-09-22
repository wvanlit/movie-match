import json
import os
# Get Movies
file = open('../data/movies.json', 'r')

movieList = json.loads(file.read())

# Iterate over list and put titles in a string
index = 0
movieString = 'var movieList = ['
for movie in movieList:
	title = movie['title']
	movieString += f'"{title}",'
	index += 1
	if index >= 5000:
		break
movieString += ']'

# Create file
target = open('../web/js/movieList.js', 'w')

target.write(movieString)



