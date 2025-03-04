from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

# To enable multithreading, ensure multiple Worker threads run in parallel.
# start multiple Worker instances based on THREADCOUNT.
# useD Rlock
# make sure add_url() and get_tbd_url() handle concurrency properly.
# each worker should fetch, process, and mark URLs independently.
# use join() in crawler.py to finish

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.start_time = time.time()
        self.TIME_LIMIT = 20 #added change
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {
            -1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        while True:
            # if time.time() - self.start_time > self.TIME_LIMIT:
            #     print("Worker time limit reached. Stopping crawler.")
            #     scraper.get_report()
            #     break
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)