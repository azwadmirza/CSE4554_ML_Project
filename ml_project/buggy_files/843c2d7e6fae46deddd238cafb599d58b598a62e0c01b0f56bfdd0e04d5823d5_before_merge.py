    def on_subscribe_control_clicked(self, index):
        item = index.model().data_items[index.row()]
        # skip LEGACY entries, regular torrents and personal channel
        if (u'subscribed' not in item or
                item[u'status'] == 1000 or
                item[u'state'] == u'Personal'):
            return
        status = int(item[u'subscribed'])
        public_key = item[u'public_key']
        id_ = item[u'id']

        def update_item(request_data):
            data_item_dict = index.model().data_items[index.row()]
            for key, _ in data_item_dict.items():
                if key in request_data:
                    data_item_dict[key] = request_data[key]

        request_mgr = TriblerRequestManager()
        request_mgr.perform_request("metadata/channels/%s/%i" % (public_key, id_), update_item,
                                    data={"subscribe": int(not status)}, method='POST')