    def load_from_memory(bencoded_data):
        """
        Load some bencoded data into a TorrentDef.
        :param bencoded_data: The bencoded data to decode and use as metainfo
        """
        metainfo = bdecode(bencoded_data)
        # Some versions of libtorrent will not raise an exception when providing invalid data.
        # This issue is present in 1.0.8 (included with Tribler 7.3.0), but has been fixed since at least 1.2.1.
        if metainfo is None:
            raise ValueError("Data is not a bencoded string")
        return TorrentDef.load_from_dict(metainfo)