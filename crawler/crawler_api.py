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
    worker_logger = get_logger("worker", "INFO")
    crawler_logger = get_logger("crawler", "INFO")
    SENTINEL = object()
    workers = []
    sleep_time = 0.1

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
                time.sleep(self.sleep_time)
                self.worker_logger.info(f"starting request for {url}")
                response = await client.get(url)
                return response.text
            # add more exceptions and handle them in the needed way
            # of company requirements
            # tweak the sleep time on some exceptions like timeout to throttle
            except httpx.HTTPError as errhttp:
                self.worker_logger.exception(f"Error HTTP: {url} code:{errhttp}")
                return False
            except httpx.ReadTimeout as errtimeout:
                self.worker_logger.exception(
                    "Error Timeout: %s code:%s", url, errtimeout
                )
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
                return False
            except httpx.ConnectError as errconn:
                self.worker_logger.exception(f"Error HTTP: {url} code:{errconn}")
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
                return False
            except Exception as e:
                # fmt: off
                self.worker_logger.error("------------------General error------------------------")
                self.worker_logger.exception(f"Error getting url: {url} code: {e}")
                return False

    async def filter_url(self, domain, anchor):
        if anchor.startswith("//"):
            anchor = "https:" + anchor
        elif anchor.startswith("/"):
            anchor = "https://" + domain + anchor
        if not Path(anchor).suffix and domain in urllib.parse.urlparse(anchor).netloc:
            return anchor

    async def find_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        anchors = [link["href"] for link in soup.find_all("a", href=True)]
        filtered_anchors = []
        for anchor in anchors:
            anchor = await self.filter_url(self.domain, anchor)
            if anchor:
                filtered_anchors.append(anchor)
        return filtered_anchors

    async def add_workers(self, num_workers=1):
        for i in range(num_workers):
            self.crawler_logger.debug(f"Adding worker")
            worker = asyncio.create_task(self.crawl())
            self.workers.append(worker)
            self.url_queue.put_nowait(self.SENTINEL)

    async def crawl(self, sleep_time=0.1):
        while True:
            time.sleep(sleep_time)
            url = await self.url_queue.get()

            if url is self.SENTINEL or None:
                self.url_queue.task_done()
                self.worker_logger.debug("-----------Worker finished----------")
                break
            if url in self.visited_urls:
                self.url_queue.task_done()
                continue
            try:
                html = await self._request(url)
            except Exception as e:
                self.worker_logger.error("--------------------------------------")
                # fmt: off
                self.worker_logger.exception(f"Error getting url on the main _request url: {e}")
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            self.visited_urls.add(url)
            try:
                links = await self.find_links(html)
            except Exception as e:
                self.worker_logger.error("--------------------------------------")
                self.worker_logger.exception("Error on parsing soup  url ")
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            for link in links:
                self.url_queue.put_nowait(link)

            # TODO: process html here

            self.worker_logger.info(f"Crawled {url}")
            self.worker_logger.info(f"Queued {self.url_queue.qsize()}")
            self.worker_logger.info(f"Skipped {len(self.skipped_urls)} ")
            self.worker_logger.info(f"Workers {len(self.workers)} ")
            self.worker_logger.info(f"Total {len(self.visited_urls)}")
            self.url_queue.task_done()

    async def start(self):
        self.url_queue.put_nowait(f"https://{self.domain}")
        worker = asyncio.create_task(self.crawl())
        self.workers.append(worker)
        self.url_queue.put_nowait(self.SENTINEL)
        while True:
            num_workers = len(self.workers)
            queue_size = self.url_queue.qsize()
            should_add_workers = (
                int(queue_size / 2) > num_workers
                and num_workers < self.max_worker_count
            )
            if should_add_workers:
                await self.add_workers()

            if all(worker.done() for worker in self.workers):
                break

            await asyncio.sleep(0.2)
        await asyncio.gather(*self.workers)

        # TODO: handle skipped urls

        self.crawler_logger.info("Finished crawling")

    def run(self):
        asyncio.run(self.start())
