        def update_item(request_data):
            data_item_dict = index.model().data_items[index.row()]
            for key, _ in data_item_dict.items():
                if key in request_data:
                    data_item_dict[key] = request_data[key]