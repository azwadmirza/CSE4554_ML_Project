    def get(self):
        '''List all predictors'''

        return g.mindsdb_native.get_models()