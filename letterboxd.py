import subprocess
import xml.etree.ElementTree as ET
import threading

"""
docs
https://github.com/janw/letterboxd-rss

1. generate xml feeds for each person
2. import each xml feed and parse it into a separate array of movies
3. combine and deduplicate g+t, and combine and dedupe p+n
"""

base_url = "https://letterboxd.com/"
usernames = ["petekp", "naomipetrash", "taramk", "garret"]
imdb_url = "http://www.imdb.com/title/"

# create an xml file with each person's watchlist
def generate_feed(username):
	subprocess.call(["letterboxd-rss", "-l=2000", "-o="+username+".xml", base_url+username])

# parse xml movie lists and save them to a file
def parse_feed(username):
	tree = ET.parse(username+".xml")
	root = tree.getroot()
	movie_list = []
	for elem in root:
		for subelem in elem.findall('item'):
			# pull the imdb link for each movie item
			movie_item = subelem[1].text.encode('utf-8').strip()
			# pull out the imdb ID from the url, for letterboxd upload formatting
			movie_item = movie_item.replace(imdb_url, "").replace("/", "")
			movie_list.append(movie_item)
	# save movie list to file
	with open(username+"_list.txt", "w") as file_handler:
		for movie in movie_list:
			file_handler.write("%s\n" % movie)

# import movie lists, combine g&t and p&n and deduplicate them
def combine_and_clean_lists(username, username2):
	with open(username+"_list.txt", 'r') as filehandle:
		movie_list1 = [current_movie.rstrip() for current_movie in filehandle.readlines()]
	with open(username2+"_list.txt", 'r') as filehandle:
		movie_list2 = [current_movie.rstrip() for current_movie in filehandle.readlines()]
	return list(dict.fromkeys(movie_list1 + movie_list2))

# find movies that match between lists
def find_matches_and_build_list():
	list1 = combine_and_clean_lists("petekp", "naomipetrash")
	list2 = combine_and_clean_lists("garret", "taramk")
	shared_list = set(list1) & set(list2)
	with open("shared_list.txt", "w") as file_handler:
		file_handler.write("imdbID" + "\n")
		for movie in shared_list:
			file_handler.write("%s\n" % movie)

# rolled up method to generate individual movie lists
# this is necessary because i have to wait for these two methods to finish
# before i can build the shared list - see main()
def generate_lists():
	for username in usernames:
		generate_feed(username)
		parse_feed(username)

def main():
	thread = threading.Thread(target=generate_lists)
	thread.start()
	# wait here for the movie lists to generate before continuing
	thread.join()

	find_matches_and_build_list()

if __name__ == '__main__':
    main()
