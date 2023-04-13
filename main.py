from crawler import Crawler
import asyncio


def main():
    domain = "bbc.com"
    crawler = Crawler(domain, max_worker_count=40)
    crawler.run()


if __name__ == "__main__":
    main()
