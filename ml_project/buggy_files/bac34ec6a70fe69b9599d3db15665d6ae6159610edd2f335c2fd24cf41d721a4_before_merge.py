    def get(self, name):
        '''List of predictors colums'''
        try:
            if is_custom(name):
                model = ca.custom_models.get_model_data(name)
            else:
                model = ca.mindsdb_native.get_model_data(name)
        except Exception:
            abort(404, 'Invalid predictor name')

        columns = []
        for array, is_target_array in [(model['data_analysis']['target_columns_metadata'], True),
                                       (model['data_analysis']['input_columns_metadata'], False)]:
            for col_data in array:
                column = {
                    'name': col_data['column_name'],
                    'data_type': col_data['data_type'].lower(),
                    'is_target_column': is_target_array
                }
                if column['data_type'] == 'categorical':
                    column['distribution'] = col_data["data_distribution"]["data_histogram"]["x"]
                columns.append(column)

        return columns, 200