    def on_torrent_created(self, result):
        self.window().edit_channel_create_torrent_button.setEnabled(True)
        if 'torrent' in result:
            self.add_torrent_to_channel(result['torrent'])