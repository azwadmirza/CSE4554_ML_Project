    def initialize_with_torrents(self, torrents):
        self.window().edit_channel_torrents_list.set_data_items([])

        items = []
        for result in torrents['torrents']:
            items.append((ChannelTorrentListItem, result,
                          {"show_controls": True, "on_remove_clicked": self.on_torrent_remove_clicked}))
        self.window().edit_channel_torrents_list.set_data_items(items)