    def on_add_to_channel_button_clicked(self, _):
        for row in self.selectionModel().selectedRows():
            if not row.model().is_torrent_item(row.row()):
                continue

            post_data = {"uri": index2uri(row)}
            request_mgr = TriblerRequestManager()
            request_mgr.perform_request("mychannel/torrents", self.on_torrent_added,
                                        method='PUT', data=post_data)