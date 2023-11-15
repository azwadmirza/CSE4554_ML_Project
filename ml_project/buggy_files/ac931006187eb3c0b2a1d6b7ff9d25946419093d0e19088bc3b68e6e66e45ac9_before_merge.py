    def from_unpack_list(cls, *args):
        (infohash, name, length, creation_date, num_files, comment) = args
        return TorrentInfoResponsePayload(infohash, name, length, creation_date, num_files, comment)