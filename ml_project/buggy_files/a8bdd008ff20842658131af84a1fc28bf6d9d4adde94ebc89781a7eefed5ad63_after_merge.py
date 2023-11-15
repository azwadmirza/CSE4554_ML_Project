    def on_received_channel_torrents(self, result):
        if not result:
            return
        self.torrents_in_playlist = self.playlist_info['torrents']

        self.torrents_in_channel = []
        for torrent in result['torrents']:
            if not ManagePlaylistPage.list_contains_torrent(self.torrents_in_playlist, torrent):
                self.torrents_in_channel.append(torrent)

        self.update_lists()