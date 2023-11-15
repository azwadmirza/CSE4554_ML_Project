    def get(self):
        '''List all predictors'''

        return ca.mindsdb_native.get_models()