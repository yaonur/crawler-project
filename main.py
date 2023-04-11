from crawler import Crawler

def main():
	url = 'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2&f_WRA=true&keywords=python&location=United%20States&sortBy=R'
	crawler = Crawler(url)
	crawler._request()
	jobs = crawler.get_jobs()
	print(jobs)

if __name__ == '__main__':
	main()