from crawler import Crawler

def main():
	domain="crawler-test.com"
	crawler = Crawler(domain)
	crawler.run()
	
	

if __name__ == '__main__':
	main()