import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import requests
import concurrent.futures
from objects import Torrent
from decimal import *
import re
from dateutil.parser import parse


class Provider(object):
    name = 'EZTV'
    shortname = 'EZT'
    provider_urls = ['https://eztv.ag']

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id
        self.base_url = self.provider_urls[0]

    @staticmethod
    def to_bytes(size_string):
        # 268.07 MB
        x = size_string.split(" ")[0]
        number = Decimal(x)

        if "MB" in size_string:
            return int(number * 1000000)

        if "GB" in size_string:
            return int(number * 1000000000)

    def search(self, search_string, season=None, episode=None):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        search_data = []
        loop_number = 0
        for search in searches:
            search_tpl = '{}/search/{}'
            search = search.replace(' ', '-')
            search = urllib.parse.quote(search)
            url = search_tpl.format(self.base_url, search)
            try:
                loop_number += 1
                self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                # can't connect, go to next url
                continue

            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
            search_results = soup.find_all('tr', class_='forum_header_border')
            if search_results is None:
                continue

            for tr in search_results:
                try:
                    tds = tr.find_all('td')
                    title = tds[1].get_text(strip=True)
                    if search_string.lower() not in title.lower():
                        continue
                    detail_url = tds[1].a['href']
                    magnet = tds[2].a['href']
                    if not magnet.startswith('magnet'):
                        continue
                    size = tds[3].get_text(strip=True)
                    date = tds[4].get_text(strip=True)
                except TypeError:
                    continue

                search_data.append([detail_url, title, date, magnet, size])

        torrents = []

        # ASYNCHRONOUS
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            res = {
                executor.submit(self._get_details, torrent): torrent for torrent in search_data
            }
            for future in concurrent.futures.as_completed(res):
                details = future.result()
                torrents.append(details)

        self.logger.info('%s[%s]@%s found %s result(s)' % (self.job_id, self.shortname, loop_number,
                                                           len(torrents)))
        return torrents

    def _get_details(self, torrent):
        url = '{}{}'.format(self.base_url, torrent[0])
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            # can't connect, go to next url
            return

        html = r.content
        soup = BeautifulSoup(html, 'html.parser')
        seeds = soup.find('span', class_='stat_red')
        if seeds:
            seeds = seeds.get_text(strip=True)
            seeds = seeds.replace(',', '')
        else:
            seeds = 0

        # <b>Released:</b> 20th Aug 2016<br/>
        dt = None
        p = re.compile('.*<b>Released:</b> (.*?)<.*')
        m = p.match(str(html))

        if m:
            date_string = m.groups()[0]
            dt = parse(date_string)

        t = Torrent()
        t.title = torrent[1]
        t.size = self.to_bytes(torrent[4])
        t.date = dt
        t.seeders = int(seeds)
        t.tracker = self.shortname
        t.magnet = torrent[3]
        return t

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

        # eztv doesn't use the search_two style
        # return [search_one, search_two]
        return [search_one]
