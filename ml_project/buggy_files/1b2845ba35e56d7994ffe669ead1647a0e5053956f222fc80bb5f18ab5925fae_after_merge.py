    def delete(self, name):
        '''delete datasource'''
        try:
            ca.default_store.delete_datasource(name)
        except Exception as e:
            print(e)
            abort(400, str(e))
        return '', 200