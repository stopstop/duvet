from concurrent.futures import ThreadPoolExecutor

from urllib.parse import urlparse, parse_qs
from uuid import uuid4
import logging
import time

from duvet.search_providers import extratorrent
from duvet.search_providers import bitsnoop
from duvet.search_providers import thepiratebay_sx
from duvet.search_providers import onethreethreesevenx_to
from duvet.search_providers import rarbg_to
from duvet.search_providers import eztv_ag
from duvet.search_providers import btstorr_cc
# from duvet.search_providers import torrentdownloads_me  (Disabled because it seems dodgy?)

engines = [extratorrent, bitsnoop, thepiratebay_sx, onethreethreesevenx_to, rarbg_to, eztv_ag, btstorr_cc]


class Duvet(object):

    def __init__(self):
        self.engines = engines
        self.logger = logging.Logger('duvet')
        fh = logging.FileHandler('search.log')
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)
        self.torrents = []
        self.min_seeders = None
        self.finished = False
        self.futures = {}

    def job(self, engine, search_string, season, episode):
        job_id = uuid4().hex
        self.logger.info('%s[%s] Initiating Provider "%s"' % (job_id, engine.Provider.shortname, engine.Provider.name))
        search = engine.Provider(self.logger, job_id=job_id)
        search_results = search.search(search_string, season, episode)
        self.logger.info('%s[%s] returned "%s results"' % (job_id, engine.Provider.shortname, len(search_results)))

        if self.min_seeders:
            search_results[:] = [x for x in search_results if not x.seeders < self.min_seeders]

        self.torrents.extend(search_results)
        self._sort_torrents()

        # Process the self.futures so that we can detect when all threads have returned answers.
        del(self.futures[engine])
        if len(self.futures) == 0:
            self.finished = True

    def search(self, search_string, season=None, episode=None, min_seeders=None, remove_duplicates=True,
               wait_and_return_results=True):
        self.logger.info('Searching for "%s"  SE:%s   EP:%s  Min Seeds:%s  Remove Dupes:%s' %
                         (search_string, season, episode, min_seeders, remove_duplicates))

        self.min_seeders = min_seeders
        pool = ThreadPoolExecutor(len(self.engines))
        for engine in self.engines:
            self.futures[engine] = pool.submit(self.job, engine, search_string, season, episode)

        if wait_and_return_results:
            while not self.finished:
                time.sleep(0.1)

            self.remove_duplicates()
            return self.torrents

    def _sort_torrents(self):
        self.torrents.sort(key=lambda x: int(x.seeders), reverse=True)

    def remove_duplicates(self):
        # Remove duplicates since different sites might have the same torrent
        titles = []
        for x in self.torrents:
            title = x.title
            if title in titles:
                self.logger.info("Deleting Dupe %s" % title)
                x._remove = True
            else:
                titles.append(title)

        # Remove duplicates based on the magnet hash
        hashes = []
        for x in self.torrents:
            o = urlparse(x.magnet)
            torrent_hash = parse_qs(o.query)['xt']
            torrent_hash = torrent_hash[0].split(':')[-1]
            if torrent_hash in hashes:
                self.logger.info("Deleting Dupe %s" % torrent_hash)
                x._remove = True
            else:
                hashes.append(torrent_hash)

        self.torrents[:] = [x for x in self.torrents if not x._remove]


if __name__ == '__main__':
    print("Example where we fetch results by polling")
    d = Duvet()
    d.search(search_string="Stranger Things", season=1, episode=4, min_seeders=30, wait_and_return_results=False)

    while not d.finished:
        print("Found %s results" % len(d.torrents))
        time.sleep(0.1)

    d.remove_duplicates()

    for t in d.torrents:
        print(str(t))

    print("\n\nExample where we return results:")
    d = Duvet()
    torrents = d.search(search_string="UFC 202", min_seeders=500, wait_and_return_results=True)

    for t in torrents:
        print(str(t))
