import os
import sqlite3
import datetime
import operator

def parse(url):
	try:
		parsed_url_components = url.split('//')
		sublevel_split = parsed_url_components[1].split('/', 1)
		domain = sublevel_split[0].replace("www.", "")
		return domain
	except IndexError:
		print "Add an url in this format - https://example.org/"

#path to user's history database
data_path = os.path.expanduser('~')+"\AppData\Local\Google\Chrome\User Data\Default"
files = os.listdir(data_path)

history_db = os.path.join(data_path, 'history')
print history_db


#querying the db
c = sqlite3.connect(history_db)
cursor = c.cursor()
select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
cursor.execute(select_statement)

results = cursor.fetchall() #tuple

sites_count = {} #dict makes iterations easier :D

for url, count in results:
	url = parse(url)
	if url in sites_count:
		sites_count[url] += 1
	else:
		sites_count[url] = 1

#sorting the dict by values
sites_count_sorted = sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True)

#results
for site, count in sites_count_sorted:
	print site, count 