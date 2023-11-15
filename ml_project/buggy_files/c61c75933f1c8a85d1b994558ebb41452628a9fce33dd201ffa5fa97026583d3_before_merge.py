    def set_byte_priority(self, byteranges, priority):
        pieces = []
        torrent_info = get_info_from_handle(self.handle)
        if not torrent_info:
            self._logger.info("LibtorrentDownloadImpl: could not get info from download handle")

        for fileindex, bytes_begin, bytes_end in byteranges:
            if fileindex >= 0:
                # Ensure the we remain within the file's boundaries
                file_entry = torrent_info.file_at(fileindex)
                bytes_begin = min(
                    file_entry.size, bytes_begin) if bytes_begin >= 0 else file_entry.size + (bytes_begin + 1)
                bytes_end = min(file_entry.size, bytes_end) if bytes_end >= 0 else file_entry.size + (bytes_end + 1)

                startpiece = torrent_info.map_file(fileindex, bytes_begin, 0).piece
                endpiece = torrent_info.map_file(fileindex, bytes_end, 0).piece + 1
                startpiece = max(startpiece, 0)
                endpiece = min(endpiece, torrent_info.num_pieces())

                pieces += range(startpiece, endpiece)
            else:
                self._logger.info("LibtorrentDownloadImpl: could not set priority for incorrect fileindex")

        if pieces:
            pieces = list(set(pieces))
            self.set_piece_priority(pieces, priority)