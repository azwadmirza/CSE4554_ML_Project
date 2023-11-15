    def get(self, name):
        '''return datasource metadata'''
        ds = g.default_store.get_datasource(name)
        if ds is not None:
            return ds
        return '', 404