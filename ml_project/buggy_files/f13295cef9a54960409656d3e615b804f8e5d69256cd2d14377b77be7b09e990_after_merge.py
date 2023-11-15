    def get_libtorrent_max_upload_rate(self):
        """
        Gets the maximum upload rate (kB / s).

        :return: the maximum upload rate in kB / s
        """
        return min(self.config['libtorrent'].as_int('max_upload_rate'), MAX_LIBTORRENT_RATE_LIMIT)