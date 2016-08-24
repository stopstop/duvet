import urllib.request, urllib.parse, urllib.error
import requests
from pprint import pprint as pp
import time

from duvet.objects import Torrent
from dateutil.parser import parse


# https://torrentapi.org/apidocs_v2.txt

class Provider():

    name = 'RARBG'
    shortname = 'RBG'
    provider_urls = ['https://torrentapi.org/pubapi_v2.php']
    baseurl = provider_urls[0]

    def __init__(self, logger, job_id):
        self.logger = logger
        self.job_id = job_id

    def search(self, search_string, season=None, episode=None):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        # get token for api
        url = '{}?get_token=get_token&app_id=tvoverlord'.format(self.baseurl)
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            return []

        if r.status_code == 403:
            self.url = url
            return []

        j = r.json()

        token = j['token']

        torrents = []
        count = 0
        loop_number = 0
        for search in searches:
            # the torrentapi only allows one query every two seconds
            if count > 0:
                time.sleep(2)
            count += 1

            search_tpl = '{}?mode=search&search_string={}&token={}&format=json_extended&sort=seeders&limit=100&app_id=tvoverlord'
            search_string = urllib.parse.quote(search)
            url = search_tpl.format(self.baseurl, search_string, token)

            try:
                loop_number += 1
                self.logger.info('%s[%s]@%s via "%s"' % (self.job_id, self.shortname, loop_number, url))
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                # can't connect, go to next url
                continue

            results = r.json()
            if 'error_code' in results.keys() and results['error_code'] == 20:
                continue  # no results found

            try:
                shows = results['torrent_results']
            except KeyError:
                # no results
                continue

            for show in shows:
                torrent = Torrent()
                torrent.title = show['title']
                torrent.date = parse(show['pubdate'].split(' ')[0])
                torrent.size = int(show['size'])
                torrent.seeders = int(show['seeders'])
                torrent.magnet = show['download']
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


if __name__ == '__main__':

    p = Provider()
    # results = p.search('game of thrones')
    # results = p.search('game of thrones', season=6, episode=6)
    # results = p.search('luther', season=1, episode=5)
    results = p.search('shades of blue', season=1, episode=5)
    # results = p.search('adf asdf asdf asdf asdf asd f', season=1, episode=5)
    # click.echo('>>>len', len(results))
    pp(results)
