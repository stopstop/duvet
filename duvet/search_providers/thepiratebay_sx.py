import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
import requests
from decimal import *
from dateutil.parser import parse
from datetime import datetime, timedelta

from duvet.objects import Torrent


class Provider(object):
    provider_urls = [
        'http://thepiratebay.se',
        'http://thepiratebay.org',
    ]
    name = 'The Pirate Bay'
    shortname = 'TPB'

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

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

    @staticmethod
    def to_bytes(size_string):
        x = size_string.split(" ")[1].split(u'\xa0')[0]
        number = Decimal(x)

        if "MiB" in size_string:
            return int(number * 1000000)

        if "GiB" in size_string:
            return int(number * 1000000000)

    def search(self, search_string, season=None, episode=None):
        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        torrents = []
        loop_number = 0

        for try_url in self.provider_urls:
            # urls = '%s/search/ ' % try_url
            for search in searches:

                search_string = urllib.parse.quote(search)
                url = '%s/search/%s/0/7/0' % (try_url, search_string)
                # urls += '%s/0/7/0 ' % search_string

                loop_number += 1
                self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))

                r = requests.get(url)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')

                search_results = soup.find('table', id='searchResult')

                if search_results:
                    # for each row in search results table, (skipping thead)
                    for tr in search_results.find_all('tr')[1:]:
                        tds = tr.find_all('td')[1:]

                        try:
                            torrent = Torrent()
                            torrent.tracker = self.shortname
                            torrent.title = tds[0].find('a', {'class': 'detLink'}).string.strip()
                            details = tds[0].find('font').contents[0].split(', ')

                            # hackity hack to fix TPB's use of 'Y-day'
                            date_string = details[0].replace('Uploaded ', '')

                            if 'Y-day' in date_string:
                                yesterday = datetime.now() - timedelta(days=1)
                                date_string = date_string.replace('Y-day', yesterday.strftime('%d %B %Y'))

                            if 'Today' in date_string:
                                date_string = date_string.replace('Today', datetime.now().strftime('%d %B %Y'))

                            torrent.date = parse(date_string)
                            torrent.size = self.to_bytes(details[1])
                            torrent.seeders = int(tds[1].string)
                            torrent.magnet = tds[0].find('a', href=re.compile('magnet:.*')).attrs['href']
                            torrents.append(torrent)

                        except IndexError:

                            # sometimes some fields are empty, so trying to
                            # access them throws an IndexError.  We can safely
                            # skip them.
                            pass

                    self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                                       len(torrents)))

                    if len(torrents) != 0:
                        return torrents

        # We got this far with no results
        self.logger.info('%s[%s] exiting without any results' % (self.job_id, self.shortname))
        return torrents
