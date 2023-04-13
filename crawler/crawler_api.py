import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib
from . import consts
from .utils import get_logger, check_url
from pathlib import Path
import time


class Crawler:
    worker_logger = get_logger("worker","DEBUG")
    crawler_logger = get_logger("crawler","INFO")
    workers = []

    def __init__(self, domain, max_worker_count=10):
        self.domain = domain
        self.max_worker_count = max_worker_count
        self.url_queue = asyncio.Queue()
        self.visited_urls = {"/"}
        self.skipped_urls = set()
        self.must_handle_urls = set()

    async def _request(self, url):
        async with httpx.AsyncClient() as client:
            try:
                self.worker_logger.info(f"starting request for {url}")
                response = await client.get(url)
                return response.text
            # add more exceptions and handle them in the needed way
            # of company requirements
            except httpx.HTTPError as errhttp:
                self.worker_logger.exception("Error HTTP: %s code:%s", url, errhttp)
                return False
            except httpx.ReadTimeout as errtimeout:
                self.worker_logger.exception("Error Timeout: %s code:%s", url, errtimeout)
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
                return False
            except httpx.ConnectError as errconn:
                self.worker_logger.exception("Error HTTP: %s code:%s", url, errconn)
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
                return False
            except Exception as e:
                self.worker_logger.error(
                    "------------------General error------------------------"
                )
                self.worker_logger.exception("Error getting url: %s code: %s", url, e)
                return False

    async def filter_url(self, domain, anchor):
        if anchor.startswith("//"):
            anchor = "https:" + anchor
        elif anchor.startswith("/"):
            anchor = "https://" + domain + anchor
        if not Path(anchor).suffix and domain in urllib.parse.urlparse(anchor).netloc:
            return anchor

    async def find_links(self, html):
        soup =BeautifulSoup(html, "html.parser")
        anchors = [link["href"] for link in soup.find_all("a", href=True)]
        filtered_anchors = []
        for anchor in anchors:
            anchor =await self.filter_url(self.domain, anchor)
            if anchor:
                filtered_anchors.append(anchor)
        return filtered_anchors

    async def add_workers(self, num_workers=1):
        for i in range(num_workers):
            self.crawler_logger.debug(f"Adding worker")
            worker = asyncio.create_task(self.crawl())
            self.workers.append(worker)

    async def crawl(self, sleep_time=0.1):
        while True:
            time.sleep(sleep_time)
            self.worker_logger.info("Worker getting url from queue>>>>>")
            url = await self.url_queue.get()
            self.worker_logger.info(f"Worker have url from queue: {url}")

            if url is None:
                self.url_queue.task_done()
                self.worker_logger.debug("------------------------------------")
                self.worker_logger.debug("-----------Worker finished----------")
                self.worker_logger.debug("------------------------------------")
                break
            if url in self.visited_urls:
                self.url_queue.task_done()
                continue
            try:
                html = await self._request(url)
            except Exception as e:
                self.worker_logger.error("--------------------------------------")
                self.worker_logger.exception(
                    "Error getting url on the main _request url: %s", e
                )
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            self.visited_urls.add(url)
            try:
                links =await self.find_links(html)
            except Exception as e:
                self.worker_logger.error("--------------------------------------")
                self.worker_logger.exception("Error on parsing soup  url ")
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            for link in links:
                self.url_queue.put_nowait(link)

            # TODO: process html here

            num_workers = len(self.workers)
            queue_size = self.url_queue.qsize()
            should_add_workers = (
                int(queue_size / 2) > num_workers
                and num_workers < self.max_worker_count
            )
            if should_add_workers:
                # TODO: Maybe extend the limit of workers on some condition
                # like the site is giving very fast responses
                await self.add_workers()

            self.worker_logger.info("Crawled %s", url)
            self.worker_logger.info("Queued %s", queue_size)
            self.worker_logger.info("Skipped %s", len(self.skipped_urls))
            self.worker_logger.info("Workers %s", num_workers)
            self.worker_logger.info("Total %s", len(self.visited_urls))
            self.url_queue.task_done()

    async def start(self):
        self.url_queue.put_nowait(f"https://{self.domain}")
        worker = asyncio.create_task(self.crawl())
        self.workers.append(worker)
        await asyncio.gather(*self.workers)
        # TODO: handle skipped urls
        self.crawler_logger.info("Finished crawling")

    def run(self):
        asyncio.run(self.start())
        self.crawler_logger.info("After run----------------------------------")
