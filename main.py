from crawler import Crawler
import asyncio

def main():
	domain="crawler-test.com"
	crawler = Crawler(domain,max_worker_count=80)
	crawler.run()

if __name__ == '__main__':
	main()