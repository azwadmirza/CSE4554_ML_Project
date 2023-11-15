        def on_row_update_results(response):
            if not response:
                return
            data_item_dict = index.model().data_items[index.row()]
            for key, _ in data_item_dict.items():
                if key in response:
                    data_item_dict[key] = response[key]
            self.info_changed.emit([data_item_dict])