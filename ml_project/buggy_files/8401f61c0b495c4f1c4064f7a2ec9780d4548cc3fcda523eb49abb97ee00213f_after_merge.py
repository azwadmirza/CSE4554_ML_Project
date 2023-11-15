    def __init__(self):

        TorrentProvider.__init__(self, "Rarbg")

        self.public = True
        self.minseed = None
        self.ranked = None
        self.sorting = None
        self.minleech = None
        self.token = None
        self.token_expires = None

        # Spec: https://torrentapi.org/apidocs_v2.txt
        self.url = "https://rarbg.to"
        self.urls = {"api": "http://torrentapi.org/pubapi_v2.php"}

        self.proper_strings = ["{{PROPER|REPACK}}"]

        self.cache = tvcache.TVCache(self, min_time=10)  # only poll RARBG every 10 minutes max