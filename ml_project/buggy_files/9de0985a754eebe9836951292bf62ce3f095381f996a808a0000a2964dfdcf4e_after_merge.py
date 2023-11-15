    def post(self, name):
        '''Queries predictor'''
        global model_swapping_map

        data = request.json

        when = data.get('when') or {}
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

        # Not the fanciest semaphor, but should work since restplus is multi-threaded and this condition should rarely be reached
        while name in model_swapping_map and model_swapping_map[name] is True:
            time.sleep(1)

        results = ca.mindsdb_native.predict(name, when=when, **kwargs)
        # return '', 500
        return preparse_results(results, format_flag)