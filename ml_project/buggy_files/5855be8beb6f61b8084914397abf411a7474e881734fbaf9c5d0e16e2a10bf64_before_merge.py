    def on_playlist_torrent_removed(self, result, torrent):
        self.remove_torrent_from_playlist(torrent)