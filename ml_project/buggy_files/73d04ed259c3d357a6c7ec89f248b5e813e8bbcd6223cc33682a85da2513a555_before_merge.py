    def get(self, name):
        ds = g.default_store.get_datasource(name)
        if ds is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        analysis = g.default_store.get_analysis(ds['source'])

        return analysis, 200