    def post(self, name):
        global model_swapping_map
        data = request.json

        from_data = g.default_store.get_datasource_obj(data.get('data_source_name'))

        try:
            format_flag = data.get('format_flag')
        except:
            format_flag = 'explain'

        try:
            kwargs = data.get('kwargs')
        except:
            kwargs = {}

        if type(kwargs) != type({}):
            kwargs = {}

        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            from_data = data.get('when_data')
        if from_data is None:
            abort(400, 'No valid datasource given')

        # Not the fanciest semaphor, but should work since restplus is multi-threaded and this condition should rarely be reached
        while name in model_swapping_map and model_swapping_map[name] is True:
            time.sleep(1)

        results = g.mindsdb_native.predict(name, when_data=from_data, **kwargs)
        return preparse_results(results, format_flag)