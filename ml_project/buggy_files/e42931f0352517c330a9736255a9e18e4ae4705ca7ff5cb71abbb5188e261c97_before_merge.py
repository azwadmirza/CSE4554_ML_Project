    def is_private(self):
        """
        Returns whether this TorrentDef is a private torrent (and is not announced in the DHT).
        """
        return int(self.metainfo[b'info'].get(b'private', 0)) == 1