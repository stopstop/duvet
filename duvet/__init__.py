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

    def job(self, engine, search_string, season, episode):
        job_id = uuid4().hex
        self.logger.info('%s[%s] Initiating Provider "%s"' % (job_id,engine.Provider.shortname, engine.Provider.name))
        search = engine.Provider(self.logger, job_id=job_id)
        search_results = search.search(search_string, season, episode)
        self.logger.info('%s[%s] returned "%s results"' % (job_id, engine.Provider.shortname, len(search_results)))
        return search_results

    def search(self, search_string, season=None, episode=None, min_seeders=None, remove_duplicates=True):
        self.logger.info('Initiating Duvet Search Object')
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

        search_results = self._sort_torrents(search_results)

        if remove_duplicates:
            search_results = self._remove_duplicates(search_results)

        if min_seeders and isinstance(min_seeders, int):
            search_results = self._remove_low_seeders(search_results, min_seeders)

        return search_results

    @staticmethod
    def _sort_torrents(torrents):
        torrents.sort(key=lambda x: int(x.seeders), reverse=True)
        return torrents

    @staticmethod
    def _remove_low_seeders(torrents, min_seeders):
        out = []
        for i, torrent in enumerate(torrents):
            if torrent.seeders > min_seeders:
                out.append(torrent)
        return out

    @staticmethod
    def _remove_duplicates(torrents):
        # Remove duplicates since different sites might have the same torrent
        titles = []
        for i, torrent in enumerate(torrents):
            title = torrent.title
            if title in titles:
                del torrents[i]
            else:
                titles.append(title)

        # Remove duplicates based on the magnet hash
        hashes = []
        for i, torrent in enumerate(torrents):
            o = urlparse(torrent.magnet)
            torrent_hash = parse_qs(o.query)['xt']
            torrent_hash = torrent_hash[0].split(':')[-1]
            if torrent_hash in hashes:
                del torrents[i]
            else:
                hashes.append(torrent_hash)

        return torrents
