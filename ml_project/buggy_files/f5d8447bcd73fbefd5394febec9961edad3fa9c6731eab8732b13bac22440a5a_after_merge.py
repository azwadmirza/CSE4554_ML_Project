    def check_torrent_health(self, data_item, forced=False):
        # TODO: stop triggering multiple checks over a single infohash by e.g. selection and click signals
        if not dict_item_is_any_of(data_item, 'type', [REGULAR_TORRENT]):
            return

        infohash = data_item[u'infohash']

        if u'health' not in self.model.column_position:
            return
        # Check if the entry still exists in the table
        row = self.model.item_uid_map.get(infohash)
        if row is None:
            return
        data_item = self.model.data_items[row]
        if not forced and data_item.get('health', HEALTH_UNCHECKED) != HEALTH_UNCHECKED:
            return
        data_item[u'health'] = HEALTH_CHECKING
        health_cell_index = self.model.index(row, self.model.column_position[u'health'])
        self.model.dataChanged.emit(health_cell_index, health_cell_index, [])

        TriblerNetworkRequest(
            "metadata/torrents/%s/health" % infohash,
            self.on_health_response,
            url_params={"nowait": True, "refresh": True},
            capture_core_errors=False,
            priority=QNetworkRequest.LowPriority,
        )