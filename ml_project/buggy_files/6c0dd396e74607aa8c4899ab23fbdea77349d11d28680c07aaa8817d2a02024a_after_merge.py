    def __init__(self, infohash, num_seeders, num_leechers, timestamp):
        super(TorrentHealthPayload, self).__init__()
        self.infohash = infohash
        self.num_seeders = num_seeders or 0
        self.num_leechers = num_leechers or 0
        self.timestamp = timestamp or -1