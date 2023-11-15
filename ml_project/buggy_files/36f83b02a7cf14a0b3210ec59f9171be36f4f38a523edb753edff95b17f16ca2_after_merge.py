        def on_row_update_results(response):
            if not response:
                return
            item_row = self.item_uid_map.get(combine_pk_id(public_key, id_))
            if item_row is None:
                return
            data_item_dict = index.model().data_items[item_row]
            data_item_dict.update(response)
            self.info_changed.emit([data_item_dict])