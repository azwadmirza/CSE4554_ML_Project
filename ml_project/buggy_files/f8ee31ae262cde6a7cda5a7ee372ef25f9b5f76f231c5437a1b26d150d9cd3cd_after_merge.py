    def on_torrents_remove_selected_action(self, action, items):
        if action == 0:

            if isinstance(items, list):
                infohash = ",".join([torrent_item.torrent_info['infohash'] for torrent_item in items])
            else:
                infohash = items.torrent_info['infohash']
            self.editchannel_request_mgr = TriblerRequestManager()
            self.editchannel_request_mgr.perform_request("channels/discovered/%s/torrents/%s" %
                                                         (self.channel_overview["identifier"],
                                                          infohash),
                                                         self.on_torrent_removed, method='DELETE')

        self.dialog.setParent(None)
        self.dialog = None