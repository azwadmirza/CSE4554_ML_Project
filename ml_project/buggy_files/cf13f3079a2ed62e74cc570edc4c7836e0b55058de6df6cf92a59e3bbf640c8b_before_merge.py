    def __init__(self):
        """Initialize the class."""
        super(YggtorrentProvider, self).__init__('Yggtorrent')

        # Credentials
        self.username = None
        self.password = None

        # URLs
        self.url = 'https://ww4.yggtorrent.is'
        self.urls = {
            'auth': urljoin(self.url, 'user/ajax_usermenu'),
            'login': urljoin(self.url, 'user/login'),
            'search': urljoin(self.url, 'engine/search'),
            'download': urljoin(self.url, 'engine/download_torrent?id={0}')
        }

        # Proper Strings
        self.proper_strings = ['PROPER', 'REPACK', 'REAL', 'RERIP']

        # Torrent Stats
        self.minseed = None
        self.minleech = None

        # Cache
        self.cache = tv.Cache(self, min_time=20)