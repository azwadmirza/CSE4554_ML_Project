    def get(self):
        '''List all datasources'''
        return g.default_store.get_datasources()