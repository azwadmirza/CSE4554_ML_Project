    def setData(self, index, new_value, role=None):
        if role != Qt.EditRole:
            return True
        public_key = self.data_items[index.row()][u'public_key']
        id_ = self.data_items[index.row()][u'id']
        attribute_name = self.columns[index.column()]
        attribute_name = u'tags' if attribute_name == u'category' else attribute_name
        attribute_name = u'title' if attribute_name == u'name' else attribute_name
        attribute_name = u'subscribed' if attribute_name == u'votes' else attribute_name

        def on_row_update_results(response):
            if not response:
                return
            data_item_dict = index.model().data_items[index.row()]
            for key, _ in data_item_dict.items():
                if key in response:
                    data_item_dict[key] = response[key]
            self.info_changed.emit([data_item_dict])

        TriblerNetworkRequest(
            "metadata/%s/%s" % (public_key, id_),
            on_row_update_results,
            method='PATCH',
            raw_data=json.dumps({attribute_name: new_value}),
        )

        # TODO: reload the whole row from DB instead of just changing the displayed value
        self.data_items[index.row()][self.columns[index.column()]] = new_value
        return True