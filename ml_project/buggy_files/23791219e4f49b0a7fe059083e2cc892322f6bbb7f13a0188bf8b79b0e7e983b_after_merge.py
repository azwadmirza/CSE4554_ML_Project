    def on_metadata_received_alert(self, alert):
        torrent_info = get_info_from_handle(self.handle)
        if not torrent_info:
            return

        metadata = {b'info': bdecode_compat(torrent_info.metadata())}

        trackers = [ensure_binary(tracker['url']) for tracker in self.handle.trackers()]
        if trackers:
            if len(trackers) > 1:
                metadata[b"announce-list"] = [trackers]
            else:
                metadata[b"announce"] = trackers[0]

        try:
            self.tdef = TorrentDef.load_from_dict(metadata)
        except ValueError as ve:
            self._logger.exception(ve)
            return

        try:
            torrent_files = lt.torrent_info(metadata).files()
        except RuntimeError:
            self._logger.warning("Torrent contains no files!")
            torrent_files = []

        self.orig_files = [ensure_text(torrent_file.path) for torrent_file in torrent_files]
        self.set_corrected_infoname()
        self.set_filepieceranges()
        self.set_selected_files()

        self.checkpoint()