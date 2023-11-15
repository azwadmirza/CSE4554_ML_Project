    def log_statistics(self):
        """Log transfer statistics"""
        lt_torrents = self.session.lm.ltmgr.get_session().get_torrents()

        for lt_torrent in lt_torrents:
            status = lt_torrent.status()

            if unhexlify(str(status.info_hash)) in self.torrents:
                self._logger.debug("Status for %s : %s %s | ul_lim : %d, max_ul %d, maxcon %d", status.info_hash,
                                   status.all_time_download, status.all_time_upload, lt_torrent.upload_limit(),
                                   lt_torrent.max_uploads(), lt_torrent.max_connections())

                # piece_priorities will fail in libtorrent 1.0.9
                if lt.__version__ == '1.0.9.0':
                    continue
                else:
                    non_zero_values = []
                    for piece_priority in lt_torrent.piece_priorities():
                        if piece_priority != 0:
                            non_zero_values.append(piece_priority)
                    if non_zero_values:
                        self._logger.debug("Non zero priorities for %s : %s", status.info_hash, non_zero_values)