    def selection_can_be_added_to_channel(self):
        for row in self.table_view.selectionModel().selectedRows():
            data_item = row.model().data_items[row.row()]
            if dict_item_is_any_of(data_item, 'type', [REGULAR_TORRENT, CHANNEL_TORRENT, COLLECTION_NODE]):
                return True
        return False