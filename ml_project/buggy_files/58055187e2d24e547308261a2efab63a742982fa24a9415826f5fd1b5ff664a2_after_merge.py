    def get_model_data(self, name, native_view=False):
        model = F.get_model_data(name)
        if native_view:
            return model

        data_analysis = model['data_analysis_v2']
        for column in data_analysis['columns']:
            if len(data_analysis[column]) == 0 or data_analysis[column].get('empty', {}).get('is_empty', False):
                data_analysis[column]['typing'] = {
                    'data_subtype': DATA_SUBTYPES.INT
                }

        return model