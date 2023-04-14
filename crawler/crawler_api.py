import asyncio
import time
import urllib
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from . import consts
from .utils import get_logger


class Crawler:
    worker_logger = get_logger("worker", "worker", "INFO")
    crawler_logger = get_logger("crawler", "crawler", "INFO")
    SENTINEL = object()
    workers = []

    def __init__(self, domain, max_worker_count=10, sleep_time=0.1):
        self.domain = domain
        self.max_worker_count = max_worker_count
        self.url_queue = asyncio.Queue()
        self.visited_urls = {"/"}
        self.skipped_urls = set()
        self.must_handle_urls = set()
        self.sleep_time = sleep_time

    async def _request(self, url):
        async with httpx.AsyncClient() as client:
            try:
                time.sleep(self.sleep_time)
                self.worker_logger.info("starting request for %s", url)
                response = await client.get(url, headers=consts.HEADERS)
                return response.text
            # add more exceptions and handle them in the needed way
            # of company requirements
            # tweak the sleep time on some exceptions like timeout to throttle
            except httpx.ConnectTimeout:
                self.worker_logger.error("Error ConnectionTimout: %s", url)
                self.skipped_urls.add(url)
            except httpx.ReadTimeout as err:
                self.worker_logger.error("Error Timeout: %s code:%s", url, err)
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
            except httpx.ConnectError as err:
                self.worker_logger.error("Error Connect: %s code: %s", url, err)
                self.worker_logger.error("adding to skipped urls")
                self.skipped_urls.add(url)
            except httpx.HTTPError as err:
                self.worker_logger.error("Error HTTP: %s code: %s", url, err)
            except Exception as err:
                # fmt: off
                self.worker_logger.exception("----------------General error----------------------")
                self.worker_logger.exception("Error getting url: %s code: %s", url, err)

    async def filter_url(self, domain, anchor):
        filtered_extensions = [
            ".pdf",
            ".jpg",
            ".png",
            ".jpeg",
            ".gif",
            ".svg",
            ".mpeg",
            ".mp4",
        ]
        filtered_startswith = [
            "mailto:",
            "skype:",
            "whatsapp:",
            "viber:",
            "sms:",
            "ftp:",
        ]
        for startswith in filtered_startswith:
            if anchor.startswith(startswith):
                return None
        if anchor.startswith("//"):
            anchor = "https:" + anchor
        elif anchor.startswith("/"):
            anchor = "https://" + domain + anchor

        if (
            Path(anchor).suffix  not in filtered_extensions
            and domain in urllib.parse.urlparse(anchor).netloc
        ):
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
        for _ in range(num_workers):
            self.crawler_logger.debug("Adding worker")
            worker = asyncio.create_task(self.crawl())
            self.workers.append(worker)
            self.url_queue.put_nowait(self.SENTINEL)

    async def remove_workers(self, num_workers=1):
        for _ in range(num_workers):
            worker = self.workers.pop()
            worker.cancel()

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
                if not html:
                    continue
            except Exception as err:
                self.worker_logger.error("--------------------------------------")
                # fmt: off
                self.worker_logger.exception("Error getting url on the main _request url: %s",err)
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            self.visited_urls.add(url)

            try:
                links = await self.find_links(html)
            except Exception as err:
                self.worker_logger.error("--------------------------------------")
                self.worker_logger.exception("Error on parsing soup url: %s", err)
                self.must_handle_urls.add(url)
                self.url_queue.task_done()
                continue
            for link in links:
                self.url_queue.put_nowait(link)

            # TODO: process html here

            self.worker_logger.info("Crawled: %s", url)
            self.worker_logger.info("Queued: %s ", self.url_queue.qsize())
            self.worker_logger.info("Skipped: %s", len(self.skipped_urls))
            self.worker_logger.info("Workers: %s", len(self.workers))
            self.worker_logger.info("Total: %s", len(self.visited_urls))
            self.url_queue.task_done()

    async def start(self):
        self.url_queue.put_nowait(f"https://{self.domain}")
        self.url_queue.put_nowait(f"https://www.{self.domain}")
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
        # TODO: scale down on some conditions maybe when getting too many timeout errors
        self.crawler_logger.info("Waiting for workers to finish")
        await asyncio.gather(*self.workers)

        # TODO: handle skipped urls

        self.crawler_logger.info("Finished crawling")

    def run(self):
        try:
            asyncio.run(self.start())
        except Exception as err:
            self.crawler_logger.exception("Error on running crawler")
            self.crawler_logger.exception(err)
            # TODO: big time failure maybe send to sentry ,restart the crawler etc.
            raise Exception("Disco")
