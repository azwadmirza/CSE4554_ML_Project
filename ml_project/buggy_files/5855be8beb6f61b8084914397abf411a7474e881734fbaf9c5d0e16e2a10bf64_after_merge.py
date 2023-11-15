    def on_playlist_torrent_removed(self, result, torrent):
        if not result:
            return
        self.remove_torrent_from_playlist(torrent)