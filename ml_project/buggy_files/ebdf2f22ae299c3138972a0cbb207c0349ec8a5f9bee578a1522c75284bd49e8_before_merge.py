    def on_commit_control_clicked(self, index):
        infohash = index.model().data_items[index.row()][u'infohash']
        status = index.model().data_items[index.row()][u'status']

        new_status = COMMIT_STATUS_COMMITTED
        if status == COMMIT_STATUS_NEW or status == COMMIT_STATUS_COMMITTED:
            new_status = COMMIT_STATUS_TODELETE

        request_mgr = TriblerRequestManager()
        request_mgr.perform_request("mychannel/torrents/%s" % infohash,
                                    lambda response: self.on_torrent_status_updated(response, index),
                                    data={"status": new_status}, method='PATCH')