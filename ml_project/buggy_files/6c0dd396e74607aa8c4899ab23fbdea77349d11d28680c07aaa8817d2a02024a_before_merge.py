    def __init__(self, infohash, num_seeders, num_leechers, timestamp):
        super(TorrentHealthPayload, self).__init__()
        self._infohash = infohash
        self._num_seeders = num_seeders
        self._num_leechers = num_leechers
        self._timestamp = timestamp