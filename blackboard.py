import requests
from bs4 import BeautifulSoup
import queue
from pathlib import Path
from time import sleep
from datetime import datetime
import urllib
import json

user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

headers={
	"User-Agent":user_agent
}
skipped_urls=[]
def find_links(parsed_html,base_url):
	anchors = [link["href"] for link in soup.find_all('a',href=True) if domain in urllib.parse.urlparse(link["href"]).netloc]
	return anchors

def find_links_test(parsed_html,base_url):
	anchors = [link["href"] for link in soup.find_all('a',href=True)]
	return anchors


base_url="https://www.linkedin.com"
domain="linkedin.com"
base_url="https://crawler-test.com"
domain="crawler-test.com"
url=""
links=[]
urls=["/"]
queued_anchors=queue.Queue()
skipped_urls=[]

def check_url(anchor):
	if Path(anchor).suffix:
		return False
	elif anchor.startswith("//"):
		return "https:"+anchor
	elif anchor.startswith("/"):
		return base_url+anchor
	elif domain in urllib.parse.urlparse(anchor).netloc:
		return anchor
	return False

start_time=datetime.now()

while True:
	if not url:
		url=base_url
		urls.append(url)

	
	try:
		resp=requests.get(url,headers=headers)
		resp.raise_for_status()
	except Exception as e:
		print(f"-------------ERROR: {e}-------------")
		skipped_urls.append(url)
		url=queued_anchors.get()
		continue

	soup=BeautifulSoup(resp.content, "html.parser")
	sleep(.1)
	anchors=find_links_test(soup,url)
	if anchors:
		for link in anchors:
			link=check_url(link)
			if not link or link in urls:
				continue
			urls.append(link)
			queued_anchors.put(link)
	if queued_anchors.empty():
		break
	url=queued_anchors.get()
	print("starting new anchor")
	print(f"length of urls: {len(urls)}")
	print(f"length of queued_anchors: {queued_anchors.qsize()}")
	print(f"length of skipped_urls: {len(skipped_urls)}")
	print(f"time elapsed: {datetime.now()-start_time}")
	print(url)

end_time=datetime.now()
print(f"time: {end_time-start_time}")
crawler_data={
	"start_time":start_time.isoformat(),
	"end_time":end_time.isoformat(),
	"time_elapsed":str(end_time-start_time),
	"crawled_url_num":len(urls),
	"urls":urls,
}

with open('links.json', 'w') as file:
    # Write the data to the file
    json.dump(crawler_data, file)

def ninka():
	anchors = [link for link in soup.find_all('a') if link.has_attr('href') and domain in urllib.parse.urlparse(link['href']).netloc and not Path(anchor).suffix]