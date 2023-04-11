from requests import Session
from bs4 import BeautifulSoup
import crawler.consts

class Crawler:
	def __init__(self, url):
		self.url = url
		self.session = Session()
		self.soup = None
		self.user_agent = crawler.consts.USER_AGENT

	def _request(self):
		resp = self.session.get(self.url)
		response.raise_for_status()
		self.soup = BeautifulSoup(resp.content, "html.parser")

	