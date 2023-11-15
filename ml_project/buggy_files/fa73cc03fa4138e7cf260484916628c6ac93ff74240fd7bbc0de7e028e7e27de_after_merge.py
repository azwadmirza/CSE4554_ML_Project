    def on_torrent_to_channel_added(self, result):
        if not result:
            return
        if 'added' in result:
            self.load_channel_torrents()