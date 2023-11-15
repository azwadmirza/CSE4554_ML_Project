    def get(self):
        """Will return the additional data keys and the dict."""

        self.progress.new('Recovering additional keys and data for %s' % self.target)
        self.progress.update('...')
        database = db.DB(self.db_path, utils.get_required_version_for_db(self.db_path))
        additional_data = database.get_table_as_dict(self.table_name)
        additional_data_keys = database.get_single_column_from_table(self.table_name, 'data_key', unique=True)
        additional_data_item_names = database.get_single_column_from_table(self.table_name, 'item_name', unique=True)
        database.disconnect()

        if not len(additional_data_item_names):
            self.progress.end()
            return [], {}

        d = {}
        for additional_data_item_name in additional_data_item_names:
            d[additional_data_item_name] = {}

        for entry in additional_data.values():
            additional_data_item_name = entry['item_name']
            key = entry['data_key']
            value = entry['data_value']

            if entry['data_type'] in ['int', 'float']:
                d[additional_data_item_name][key] = eval(entry['data_type'])(value)
            else:
                d[additional_data_item_name][key] = value

        for additional_data_item_name in d:
            for key in additional_data_keys:
                if key not in d[additional_data_item_name]:
                    d[additional_data_item_name][key] = None

        self.progress.end()

        return additional_data_keys, d