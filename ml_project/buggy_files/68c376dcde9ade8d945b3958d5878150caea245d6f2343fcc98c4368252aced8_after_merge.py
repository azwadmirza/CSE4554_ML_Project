    def __init__(self):
        """Initialize the class."""
        super(self.__class__, self).__init__('LimeTorrents')

        # Credentials
        self.public = True

        # URLs
        self.url = 'https://www.limetorrents.cc'
        self.urls = {
            'update': urljoin(self.url, '/post/updatestats.php'),
            'search': urljoin(self.url, '/search/tv/{query}/'),
            'rss': urljoin(self.url, '/browse-torrents/TV-shows/date/{page}/'),
        }

        # Proper Strings
        self.proper_strings = ['PROPER', 'REPACK', 'REAL']

        # Miscellaneous Options
        self.confirmed = False

        # Torrent Stats
        self.minseed = None
        self.minleech = None

        # Cache
        self.cache = tv_cache.TVCache(self, min_time=10)