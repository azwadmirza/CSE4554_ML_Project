    def put(self, name):
        '''Learning new predictor'''
        global model_swapping_map

        data = request.json
        to_predict = data.get('to_predict')

        try:
            kwargs = data.get('kwargs')
        except:
            kwargs = None

        if type(kwargs) != type({}):
            kwargs = {}

        if 'stop_training_in_x_seconds' not in kwargs:
            kwargs['stop_training_in_x_seconds'] = 100

        if 'equal_accuracy_for_all_output_categories' not in kwargs:
            kwargs['equal_accuracy_for_all_output_categories'] = True

        if 'sample_margin_of_error' not in kwargs:
            kwargs['sample_margin_of_error'] = 0.005

        if 'unstable_parameters_dict' not in kwargs:
            kwargs['unstable_parameters_dict'] = {}

        if 'use_selfaware_model' not in kwargs['unstable_parameters_dict']:
            kwargs['unstable_parameters_dict']['use_selfaware_model'] = False

        try:
            retrain = data.get('retrain')
            if retrain in ('true', 'True'):
                retrain = True
            else:
                retrain = False
        except:
            retrain = None

        ds_name = data.get('data_source_name') if data.get('data_source_name') is not None else data.get('from_data')
        from_data = g.default_store.get_datasource_obj(ds_name)

        if retrain is True:
            original_name = name
            name = name + '_retrained'

        g.mindsdb_native.learn(name, from_data, to_predict, kwargs)

        if retrain is True:
            try:
                model_swapping_map[original_name] = True
                g.mindsdb_native.delete_model(original_name)
                g.mindsdb_native.rename_model(name, original_name)
                model_swapping_map[original_name] = False
            except:
                model_swapping_map[original_name] = False

        return '', 200