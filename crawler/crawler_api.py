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
		self.soup = BeautifulSoup(resp.content, "html.parser")

	def get_job_list(self):
		return self.soup.find('ul', class_='jobs-search__results-list').find_all('li')

	def get_job_title(self, job):
		return job.find('h3', class_='base-search-card__title').text.strip()

	def get_job_company(self, job):
		return job.find('h4', class_='base-search-card__subtitle').text.strip()

	def get_job_location(self, job):
		return job.find('span', class_='job-search-card__location').text.strip()

	def get_job_time(self, job):
		return job.find('time').text.strip()

	def get_job_link(self, job):
		return job.find('a')['href']


	def get_job(self, job):
		return {
			'title': self.get_job_title(job),
			'company': self.get_job_company(job),
			'location': self.get_job_location(job),
			'link': self.get_job_link(job),
			'time': self.get_job_time(job)
		}
	def get_job_description(self, job):
		job_link = self.get_job_link(job)
		resp = self.session.get(job_link)
		soup = BeautifulSoup(resp.content, "html.parser")
		return soup.find('div', class_='description__text description__text--rich').text.strip()

	def get_jobs(self):
		jobs = []
		for job in self.get_job_list():
			jobs.append(self.get_job(job))
		return jobs