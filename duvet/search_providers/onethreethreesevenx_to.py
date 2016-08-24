import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import requests
from decimal import *
import dateparser  # TODO Why does this slow down our execution by about 1 second ???

import concurrent.futures
from duvet.objects import Torrent


class Provider(object):
    name = '1337X'
    shortname = '13X'
    provider_urls = ['http://1337x.to']
    base_url = provider_urls[0]

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

    @staticmethod
    def to_bytes(size_string):
        # 1,002.43 MB
        x = size_string.split(" ")[0].replace(',', '')
        number = Decimal(x)

        if "MB" in size_string:
            return int(number * 1000000)

        elif "GB" in size_string:
            return int(number * 1000000000)

    def search(self, search_string, season=None, episode=None):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        search_data = []
        loop_number = 0
        for search in searches:
            search_tpl = '{}/sort-search/{}/seeders/desc/1/'
            search_string = urllib.parse.quote(search)
            url = search_tpl.format(self.base_url, search_string)

            try:
                loop_number += 1
                self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                # can't connect, go to next url
                continue

            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
            search_results = soup.find('div', class_='tab-detail')

            if search_results:

                for li in search_results.find_all('li'):
                    divs = li.find_all('div')
                    try:
                        detail_url = divs[0].strong.a['href']
                        title = divs[0].get_text(strip=True)
                        seeds = divs[1].get_text(strip=True)
                        size = divs[3].get_text(strip=True)
                    except IndexError:
                        continue

                    search_data.append([detail_url, title, seeds, size])

                self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                                      len(search_data)))
        torrents = []

        # ASYNCHRONOUS
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            res = {
                executor.submit(self._get_details, detail_data): detail_data for detail_data in search_data
            }
            for future in concurrent.futures.as_completed(res):
                details = future.result()
                torrents.append(details)

        self.logger.info('%s[%s]@%s fetched details for %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                                         len(torrents)))
        return torrents

    def _get_details(self, detail):
        url = '{}{}'.format('http://1337x.to', detail[0])

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            # can't connect, go to next url
            return

        html = r.content
        soup = BeautifulSoup(html, 'html.parser')
        section = soup.find('div', class_='category-detail')
        magnet = section.find_all('a')[1]['href']

        date_string = section.find_all('span')[7].get_text(strip=True)  # TODO: That's brave.
        dt = dateparser.parse(date_string)

        torrent = Torrent()
        torrent.title = detail[1]
        torrent.size = self.to_bytes(detail[3])
        torrent.date = dt
        torrent.seeders = int(detail[2])
        torrent.magnet = magnet
        torrent.tracker = self.shortname
        return torrent

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
