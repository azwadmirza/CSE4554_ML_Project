    def is_torrent_item(self, row_id):
        data_item = self.data_item.data_items[row_id]
        if u'infohash' in data_item or (u'type' in data_item and data_item[u'type'] == u'torrent'):
            return True
        return False