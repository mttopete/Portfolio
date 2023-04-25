import sys
import stat_tracker
from configparser import ConfigParser
from argparse import ArgumentParser
import PartA
from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

def main(config_file, restart):
    stat_tracker.init()
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()
    with open("results.txt",'w') as f:
        sys.stdout = f
        print("Longest Page: ", stat_tracker.longest_page)
        for word in stat_tracker.stopwords:
            try:
               del stat_tracker.word_frequency[word]
            except:
                pass
        print("Most Frequent Words: ")
        PartA.printFrequencies(stat_tracker.word_frequency)
        print("Unique Urls visited: ", len(stat_tracker.unique_urls))
        print("Ics Urls : ")
        sorted_urls = sorted(stat_tracker.ics_urls)
        for url in sorted_urls:
            print(url," - ",stat_tracker.ics_urls[url])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
