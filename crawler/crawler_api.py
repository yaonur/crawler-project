import requests
from requests import Session
from bs4 import BeautifulSoup
from . import consts
from .utils import get_logger,check_url
import queue
from pathlib import Path
from time import sleep
from datetime import datetime
import urllib

class Crawler:
	url=""
	urls=[]
	skipped_urls=[]
	def __init__(self, domain):
		self.domain = domain
		self.soup = None
		self.headers=consts.HEADERS
		self.logger = get_logger()
		self.session = Session()
		self.session.headers=self.headers
		self.urls={"/"}
		

	def _request(self,url):
		try:
			resp = self.session.get(url)
			resp.raise_for_status()
			return BeautifulSoup(resp.content, "html.parser")
		except requests.exceptions.HTTPError as errhttp:
			self.logger.exception("Error HTTP: %s code:%s", self.url,errhttp.response.status_code)
			return False
		except requests.exceptions.ReadTimeout as errtimeout:
			self.logger.exception("Error Timeout: %s code:%s", self.url,errhttp.response.status_code)
			self.logger.error("adding to skipped urls")
			self.skipped_urls.append(self.url)
			return False
		except requests.exceptions.ConnectionError as errconn:
			self.logger.exception("Error HTTP: %s code:%s", self.url,errhttp.response.status_code)
			self.logger.error("adding to skipped urls")
			self.skipped_urls.append(self.url)
			return False

	
	def find_links_test(self,parsed_html,base_url):
		anchors = [link["href"] for link in self.soup.find_all('a',href=True)]
		return anchors

	def run(self):
		queued_anchors=queue.Queue()
		while True:
			if not self.url:
				self.url=f"https://{self.domain}"
				self.urls.add(self.url)
			try:
				self.logger.info("Getting url: %s", self.url)
				soup=self._request(self.url)
				if not soup:
					self.url=queued_anchors.get()
					continue
				self.soup=soup
			except Exception as e:
				self.logger.exception("Error getting url: %s", self.url)
				self.skipped_urls.append(self.url)
				self.url=queued_anchors.get()
				continue

			anchors=self.find_links_test(soup,self.url)
			if anchors:
				for link in anchors:
					link=check_url(link,self.domain)
					if not link or link in self.urls:
						continue
					self.urls.add(link)
					queued_anchors.put(link)
			if queued_anchors.empty():
				break
			self.logger.info("Crawled %s", self.url)
			self.logger.info("Queued %s", queued_anchors.qsize())
			self.logger.info("Skipped %s", len(self.skipped_urls))
			self.logger.info("Total %s", len(self.urls))
			self.url=queued_anchors.get()

	

	