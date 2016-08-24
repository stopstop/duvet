import urllib
from time import mktime
from datetime import datetime
from decimal import *

import feedparser
from duvet.utils import sxxexx, hash2magnet
from duvet.objects import Torrent


class Provider(object):
    name = 'Bit Torrent Scene'
    provider_urls = ['http://www.btstorr.cc']
    shortname = 'BTR'

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

    @staticmethod
    def to_bytes(size_string):
        # 1.43 GB
        x = size_string.split(" ")[0]
        number = Decimal(x)

        if "MB" in size_string:
            return int(number * 1000000)

        if "GB" in size_string:
            return int(number * 1000000000)

    def search(self, search_string, season=None, episode=None):
        if season and episode:
            search_string = '%s %s' % (search_string, sxxexx(season, episode))

        query = urllib.parse.quote(search_string)

        torrents = []
        loop_number = 0

        for try_url in self.provider_urls:
            url = '%s/rss/type/search/x/%s/' % (try_url, query)
            loop_number += 1
            self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))
            parsed = feedparser.parse(url)

            for show in parsed['entries']:
                if show:
                    if show['published_parsed']:
                        dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                    else:
                        dt = None

                    t = Torrent()
                    t.title = show['title']
                    t.size = self.to_bytes(show['size'])
                    t.date = dt
                    t.seeders = int(show['seeds'])
                    t.tracker = self.shortname
                    t.magnet = hash2magnet(show['hash'], t.title)
                    torrents.append(t)

            self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                               len(torrents)))

            if len(torrents) != 0:
                return torrents

        # We got this far with no results
        self.logger.info('%s[%s] exiting without any results' % (self.job_id, self.shortname))
        return torrents
