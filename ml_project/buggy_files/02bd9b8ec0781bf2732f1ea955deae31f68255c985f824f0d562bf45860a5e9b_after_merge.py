    def get(self):
        '''List all datasources'''
        return ca.default_store.get_datasources()