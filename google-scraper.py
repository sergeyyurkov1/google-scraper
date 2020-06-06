# Importing necessary modules
from bs4 import BeautifulSoup as BS
import urllib
import requests
import re
import sys
import argparse

# Part 1
# Searching Google by keywords and extracting links to relevant articles
# ------------------------------------------------------------------------------
# Processing arguments (type python google-scraper.py --help)
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--tld", required=True, help="top level domain to restrict search to a desired territory (for example 'kz')")
ap.add_argument("-f", "--file", required=False, help="file to save results to (format: filename.csv)")
args = vars(ap.parse_args())

tld = str(args["tld"])
file = str(args["file"])

# Opens a text file to write all output to
if file:
	f = open(f"{file}", "w", encoding="utf-8")
else:
	f = open(f"comments-{tld}.txt", "w", encoding="utf-8")

# Preparing the keywords
query = f"site:.{tld} коронавирус OR covid-19 OR вирус AND китай"

# Encoding the query, translating all spaces and punctuation into a format
#Google Search will understand
query = urllib.parse.quote(query)

# Attaching the query to a search URL (the max number of results Google can
#display is 100)
URL = f"https://google.com/search?q={query}&num=100"

# Google can block the query if not made from a "real" browser, so it is
#necessary to add user agent in order to simulate a working browser
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

# Preparing headers to send with the request
headers = {"user-agent" : USER_AGENT}

# Sending the request and storing the response
resp = requests.get(URL, headers=headers)

# Checking whether URL is accessible. If yes, then scrape it
if resp.status_code == 200:
	soup = BS(resp.content, "html.parser") # use html.parser by default, other options include html5lib

# Extracting URLs from HTML and storing them in an array for use in Part 2
URLs = []

links = ""
count = 1
for g in soup.findAll("div", class_="r"):
	anchors = g.findAll("a")
	if anchors:
		link = anchors[0]["href"]
		URLs.append(link)
		links = links + str(count) + ". " + str(link) + "\n"
		count = count + 1

# Writing sanitized URLs to the text file
f.write("------------------------------------------------------------------------------\n")
f.write("Links:\n")
f.write("------------------------------------------------------------------------------\n")
f.write(str(links) + "\n")

# Part 2
# Going to URLs and scraping comments from the articles
# ------------------------------------------------------------------------------
f.write("------------------------------------------------------------------------------\n")
f.write("Articles:\n")
f.write("------------------------------------------------------------------------------\n")

for u in URLs:
	# On connection error skips to the next URL in the list
	try:
		r = requests.get(u)
	except requests.exceptions.ConnectionError:
		pass

	# Processing HTML
	soup = BS(r.content, "html5lib")
	
	# Getting the title
	title = soup.find("title")
	
	# Writing the artcle title along with its link to the file
	try:
		f.write(title.string.strip() + "\n") # Prints the tag string content
	except AttributeError:
		pass
	f.write(u + "\n")
	
	# Searching for the comment section, retrieving individual comments and writing them to the file
	# Not a perfect solution - requires a lot of manual clean-up
	regex = re.compile(".*comment.*")
	for i in soup.findAll("div", attrs = {"class":regex}):
		f.write(i.text.strip() + "\n")
	
	f.write("------------------------------------------------------------------------------\n")


