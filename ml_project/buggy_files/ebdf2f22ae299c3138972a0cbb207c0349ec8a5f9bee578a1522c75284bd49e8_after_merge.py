    def on_commit_control_clicked(self, index):
        data_item = index.model().data_items[index.row()]
        infohash = data_item[u'infohash']
        status = data_item[u'status']

        new_status = COMMIT_STATUS_COMMITTED
        if status == COMMIT_STATUS_NEW or status == COMMIT_STATUS_COMMITTED:
            new_status = COMMIT_STATUS_TODELETE

        def on_torrent_status_updated(json_result):
            if not json_result:
                return

            if 'success' in json_result and json_result['success']:
                data_item[u'status'] = json_result['new_status']
                self.window().edit_channel_page.channel_dirty = \
                    self.table_view.window().edit_channel_page.channel_dirty or \
                    (json_result['new_status'] != COMMIT_STATUS_COMMITTED)
                self.window().edit_channel_page.update_channel_commit_views(reload_view=True)

        request_mgr = TriblerRequestManager()
        request_mgr.perform_request("mychannel/torrents/%s" % infohash, on_torrent_status_updated,
                                    data={"status": new_status}, method='PATCH')