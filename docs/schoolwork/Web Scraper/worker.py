from threading import Thread, Lock
import stat_tracker as st
from utils.download import download
from utils import get_logger
from scraper import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            st.f_mutex.acquire()
            tbd_url = self.frontier.get_tbd_url()
            st.f_mutex.release()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            if tbd_url.find(".ics.uci.edu") > 0:
                st.ics_uci_edu_mutex.acquire()
                resp = download(tbd_url, self.config, self.logger)
                time.sleep(self.config.time_delay)
                st.ics_uci_edu_mutex.release()
            elif tbd_url.find(".cs.uci.edu") > 0:
                st.cs_uci_edu_mutex.acquire()
                resp = download(tbd_url, self.config, self.logger)
                time.sleep(self.config.time_delay)
                st.cs_uci_edu_mutex.release()
            elif tbd_url.find(".stat.uci.edu") > 0:
                st.stat_uci_edu_mutex.acquire()
                resp = download(tbd_url, self.config, self.logger)
                time.sleep(self.config.time_delay)
                st.stat_uci_edu_mutex.release()
            elif tbd_url.find("today.uci.edu/department/information_computer_sciences/") > 0:
                st.today_uci_edu_mutex.acquire()
                resp = download(tbd_url, self.config, self.logger)
                time.sleep(self.config.time_delay)
                st.today_uci_edu_mutex.release()
            elif tbd_url.find(".informatics.uci.edu") > 0:
                st.informatics_uci_edu_mutex.acquire()
                resp = download(tbd_url, self.config, self.logger)
                time.sleep(self.config.time_delay)
                st.informatics_uci_edu_mutex.release()
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(tbd_url, resp)
            st.f_mutex.acquire()
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            st.f_mutex.release()
