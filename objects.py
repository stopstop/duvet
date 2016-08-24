from datetime import datetime


class Torrent(object):
    def __init__(self):
        self.tracker = None
        self.url = None
        self.title = None
        self.magnet = None
        self.seeders = None
        self.leechers = None
        self.size = None
        self.date = None
        self.details = None

    def human_age(self):
        if self.date:
            age = datetime.now() - self.date
            return "%s days" % (int(age.total_seconds()/(60*60*24)))
        else:
            return "Unknown"

    def human_size(self):
        if self.size > 1000000000:
            return "%.2f GB" % (self.size / 1000000000)

        elif self.size > 1000000:
            return "%.2f MB" % (self.size/1000000)

        else:
            return "%s KB" % (self.size/1000)

    def __unicode__(self):
        return "%s   Size: %s   Seeders: %s   Age: %s   %s" % (self.title.ljust(60)[0:60], str(self.human_size()).ljust(12),
                                                               str(self.seeders).ljust(6), self.human_age(),
                                                               self.tracker)

    def __str__(self):
        return self.__unicode__()

