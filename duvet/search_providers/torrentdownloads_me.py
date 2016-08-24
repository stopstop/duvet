import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
from duvet.objects import Torrent
import feedparser

# http://www.torrentdownloads.me/rss.xml?type=search&search=Underground+S01E04


class Provider():
    name = 'Torrent Downloads'
    provider_urls = ['http://www.torrentdownloads.me']
    shortname = 'TDM'

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

    def search(self, search_string, season=None, episode=None):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        # http://www.torrentdownloads.me/rss.xml?type=search&search=doctor+who+s05e01
        base_url = '%s/rss.xml?type=search&search={}' % self.provider_urls[0]
        torrents = []
        loop_number = 0

        for search in searches:
            encoded_search = urllib.parse.quote(search)
            url = base_url.format(encoded_search)
            loop_number += 1
            self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))

            parsed = feedparser.parse(url)

            if len(parsed) == 0:
                continue

            for show in parsed['entries']:
                title = show['title']

                # torrentdownloads returns results that match any word in the
                # search, so the results end up with a bunch of stuff we aren't
                # interested in and we need to filter them out.
                stop = False
                for i in search.split(' '):
                    if i.lower() not in title.lower():
                        stop = True
                if stop:
                    continue

                dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                magnet_url = 'magnet:?xt=urn:btih:{}&dn={}'
                magnet_hash = show['info_hash']

                torrent = Torrent()
                torrent.title = show['title']
                torrent.seeders = int(show['seeders'])
                torrent.date = dt
                torrent.size = int(show['size'])
                torrent.magnet = magnet_url.format(magnet_hash, urllib.parse.quote(title))
                torrent.tracker = self.shortname

                torrents.append(torrent)

            self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                               len(torrents)))

            if len(torrents) != 0:
                return torrents

        # We got this far with no results
        self.logger.info('%s[%s] exiting without any results' % (self.job_id, self.shortname))
        return torrents


    @staticmethod
    def se_ep(show_title, season, episode):
        season = str(season)
        episode = str(episode)
        search_one = '%s S%sE%s' % (
            show_title,
            season.rjust(2, '0'),
            episode.rjust(2, '0'))

        search_two = '%s %sx%s' % (
            show_title,
            season,
            episode.rjust(2, '0'))

        return [search_one, search_two]

