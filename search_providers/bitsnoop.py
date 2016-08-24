import urllib.request
import urllib.parse
import urllib.error
import feedparser
from objects import Torrent


class Provider(object):
    provider_urls = [
        'http://bitsnoop.com',
    ]
    name = 'BitSnoop'
    shortname = 'BTS'

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

    @staticmethod
    def se_ep(season, episode, show_title):
        season_just = str(season).rjust(2, '0')
        episode = str(episode).rjust(2, '0')
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
            url = '%s/search/all/{}/c/d/1/?fmt=rss' % try_url
            full_url = url.format(encoded_search)

            loop_number += 1
            self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, full_url))
            parsed = feedparser.parse(full_url)

            for show in parsed['entries']:
                # TODO: Fetch detail pages for age of torrents
                # Removing attempts at date parsing until bitsnoop get their act together
                # if show['published_parsed']:
                #     dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                #     print(type(dt))
                #     print(dt)
                #     date = dt.strftime('%b %d/%Y')

                t = Torrent()
                t.title = show['title']
                t.size = int(show['size'])
                t.date = None
                t.seeders = int(show['numseeders'])
                t.tracker = self.shortname
                t.magnet = show['magneturi']

                torrents.append(t)

            self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                               len(torrents)))

            if len(torrents) != 0:
                return torrents

        # We got this far with no results
        self.logger.info('%s[%s] exiting without any results' % (self.job_id, self.shortname))
        return torrents
