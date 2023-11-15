    def on_torrent_to_channel_added(self, result):
        if not result:
            return
        self.window().edit_channel_create_torrent_progress_label.hide()
        if 'added' in result:
            self.window().edit_channel_details_stacked_widget.setCurrentIndex(PAGE_EDIT_CHANNEL_TORRENTS)
            self.window().edit_channel_page.load_channel_torrents()