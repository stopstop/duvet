import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
import feedparser

from objects import Torrent


class Provider(object):
    name = 'ExtraTorrent'
    shortname = 'EXT'
    provider_urls = [
        'http://fsoajdfoiajsfoasijdoasif.com'
        'http://extratorrent.cc',
        'http://etmirror.com',
        'http://etproxy.com',
        'https://extratorrent.unblocked.pe',
        'https://extratorrent.unblocked.la',
        'http://extratorrentonline.com',
        'http://extratorrent.works',
        'http://extratorrentlive.com',
    ]

    def __init__(self, logger, job_id):
        self.job_id = job_id
        self.logger = logger

    @staticmethod
    def se_ep(season, episode, show_title):
        season_just = str(season).rjust (2, '0')
        episode = str(episode).rjust (2, '0')
        fixed = '%s S%sE%s' % (
            show_title, season_just, episode)
        return fixed

    def search(self, search_string, season=False, episode=False):
        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        query = search_string
        encoded_search = urllib.parse.quote(query)

        torrents = []
        loop_number = 0

        for try_url in self.provider_urls:
            # cid=0 everything, cid=8 tv shows:
            lookfor = 0
            if season and episode:
                lookfor = 8  # tv only

            url = '{}/rss.xml?type=search&cid={}&search=%s'.format(try_url, lookfor)
            full_url = url % encoded_search
            loop_number += 1
            self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, full_url))
            parsed = feedparser.parse(full_url)

            for show in parsed['entries']:
                dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                title = show['title']

                # extratorrent returns results that match any word in the
                # search, so the results end up with a bunch of stuff we aren't
                # interested in and we need to filter them out.
                stop = False
                for i in search_string.split(' '):
                    if i.lower() not in title.lower():
                        stop = True
                if stop:
                    continue
                    # TODO: Evaluate if this is exiting early. Feels messy.

                # the ExtraTorrent rss feed doesn't supply the magnet link, or any
                # usable links (They must be downloaded from the site).  But the
                # feed has the URN hash, so we can build a magnet link from that.
                magnet_url = 'magnet:?xt=urn:btih:{}&dn={}'
                magnet_hash = show['info_hash']
                magnet = magnet_url.format(magnet_hash, urllib.parse.quote(title))
                seeds = show['seeders']
                if seeds == '---':
                    seeds = '0'

                t = Torrent()
                t.title = title
                t.size = int(show['size'])
                t.date = dt
                t.seeders = int(seeds)
                t.tracker = self.shortname
                t.magnet = magnet

                torrents.append(t)

            self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                                  len(torrents)))
            if len(torrents) != 0:
                return torrents

        # We got this far with no results
        self.logger.info('%s[%s] exiting without any results' % (self.job_id, self.shortname))
        return torrents
