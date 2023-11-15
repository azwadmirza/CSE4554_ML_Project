    def get_creation_date(self):
        """
        Returns the creation date of the torrent.
        """
        return self.metainfo.get("creation date", 0)