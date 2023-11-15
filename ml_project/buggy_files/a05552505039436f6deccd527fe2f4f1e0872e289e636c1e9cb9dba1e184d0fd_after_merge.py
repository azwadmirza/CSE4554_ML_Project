        def update_item(request_data):
            for key, _ in data_item_dict.items():
                if key in request_data:
                    data_item_dict[key] = request_data[key]