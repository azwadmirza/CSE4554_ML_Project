    def get_length(self, selectedfiles=None):
        """ Returns the total size of the content in the torrent. If the
        optional selectedfiles argument is specified, the method returns
        the total size of only those files.
        @return A length (long)
        """
        if self.metainfo:
            return maketorrent.get_length_from_metainfo(self.metainfo, selectedfiles)
        return 0