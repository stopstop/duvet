import urllib


def hash2magnet(magnet_hash, title):
    magnet_url = 'magnet:?xt=urn:btih:{}&dn={}'
    magnet = magnet_url.format(magnet_hash, urllib.parse.quote(title))
    return magnet


def sxxexx(season='', episode=''):
    """Return a season and episode formated as S01E01"""
    se = ''
    if season and episode:
        season = int(season)
        episode = int(episode)
        se = 'S%02dE%02d' % (season, episode)
    return se


def sxee(season='', episode=''):
    """Return a season and episode formated as 1X01"""
    se = ''
    if season and episode:
        season = int(season)
        episode = int(episode)
        se = '%dX%02d' % (season, episode)
    return se
