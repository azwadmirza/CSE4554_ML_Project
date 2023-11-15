    def on_torrents_remove_selected_action(self, action, item):
        if action == 0:
            self.editchannel_request_mgr = TriblerRequestManager()
            self.editchannel_request_mgr.perform_request("channels/discovered/%s/torrents/%s" %
                                                         (self.channel_overview["identifier"],
                                                          item.torrent_info['infohash']),
                                                         self.on_torrent_removed, method='DELETE')

        self.dialog.setParent(None)
        self.dialog = None