    def __init__(self, infohash, name, length, creation_date, num_files, comment):
        super(TorrentInfoResponsePayload, self).__init__()
        self._infohash = infohash
        self._name = name
        self._length = length
        self._creation_date = creation_date
        self._num_files = num_files
        self._comment = comment