from requests import Session
from bs4 import BeautifulSoup
from crawler import Crawler

session=Session()
url="https://tr.linkedin.com/jobs/software-engineer-jobs?countryRedirected=1&position=1&pageNum=0"
resp=session.get(url)
soup=BeautifulSoup(resp.content,"html.parser")
job_list = soup.find('ul', class_='jobs-search__results-list').find_all('li')

ss=job_list.find('h3', class_='base-search-card__title').text.strip()

ss=job_list.find('h4', class_='base-search-card__subtitle').text.strip()
ss=job_list.find('span', class_='job-search-card__location').text.strip()

ss=job_list.find('time').text.strip()
		
ss=job_list.find('a')['href']
