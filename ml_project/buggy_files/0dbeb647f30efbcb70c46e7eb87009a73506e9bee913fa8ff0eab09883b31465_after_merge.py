    def __init__(self, infohash, name, length, creation_date, num_files, comment):
        super(TorrentInfoResponsePayload, self).__init__()
        self.infohash = infohash
        self.name = name or ''
        self.length = length or 0
        self.creation_date = creation_date or -1
        self.num_files = num_files or 0
        self.comment = comment or ''