    def on_torrent_removed(self, json_result):
        if 'removed' in json_result and json_result['removed']:
            self.load_channel_torrents()