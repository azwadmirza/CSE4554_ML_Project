    def get_libtorrent_max_download_rate(self):
        """
        Gets the maximum download rate (kB / s).

        :return: the maximum download rate in kB / s
        """
        return min(self.config['libtorrent'].as_int('max_download_rate'), MAX_LIBTORRENT_RATE_LIMIT)