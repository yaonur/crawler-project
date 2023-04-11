import requests
from bs4 import BeautifulSoup
import queue
from pathlib import Path
from time import sleep

user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

headers={
	"User-Agent":user_agent
}

def find_links(parsed_html,base_url):
	anchors=[]
	for a in parsed_html.find_all('a', href=True):
		if a['href'].startswith(base_url):
			anchors.append(a['href'])
	return anchors


base_url="https://www.linkedin.com/"
url="https://www.linkedin.com/"
links=[]
urls=[]
queued_anchors=queue.Queue()


while True:
	if not url:
		url=base_url
	resp=requests.get(url,headers=headers)
	soup=BeautifulSoup(resp.content, "html.parser")
	sleep(1)
	anchors=find_links(soup,url)
	if anchors:
		for link in anchors:
			if link in urls:
				continue
			urls.append(link)
			if not Path(link).suffix:
				queued_anchors.put(link)
	if queued_anchors.empty():
		break
	url=queued_anchors.get()
	print("starting new anchor")
	print(f"length of urls: {len(urls)}")
	print(f"length of queued_anchors: {queued_anchors.qsize()}")
	print(url)

print(links)

