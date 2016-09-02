import concurrent.futures
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
import logging

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

    def job(self, engine, search_string, season, episode):
        job_id = uuid4().hex
        self.logger.info('%s[%s] Initiating Provider "%s"' % (job_id,engine.Provider.shortname, engine.Provider.name))
        search = engine.Provider(self.logger, job_id=job_id)
        search_results = search.search(search_string, season, episode)
        self.logger.info('%s[%s] returned "%s results"' % (job_id, engine.Provider.shortname, len(search_results)))

        # print("Response from %s" % engine.Provider.name)

        if self.min_seeders:
            search_results[:] = [x for x in search_results if not x.seeders < self.min_seeders]

        self.torrents.extend(search_results)
        self._sort_torrents()

    def search(self, search_string, season=None, episode=None, min_seeders=None, remove_duplicates=True):
        self.logger.info('Searching for "%s"  SE:%s   EP:%s  Min Seeds:%s  Remove Dupes:%s' %
                         (search_string, season, episode, min_seeders, remove_duplicates))

        self.min_seeders = min_seeders
        search_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            res = {
                executor.submit(
                    self.job, engine, search_string, season, episode
                ): engine for engine in self.engines
            }

            for future in concurrent.futures.as_completed(res):
                if future.result():
                    search_results.extend(future.result())

        # Only remove dupes once they're all in so that we keep the dupes with the highest seeders
        if remove_duplicates:
            self._remove_duplicates()

        return self.torrents

    def _sort_torrents(self):
        self.torrents.sort(key=lambda x: int(x.seeders), reverse=True)

    def _remove_duplicates(self):
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
    d = Duvet()
    r = d.search(search_string="Stranger Things", season=1, episode=4, min_seeders=30)
    for t in r:
        print(str(t))
