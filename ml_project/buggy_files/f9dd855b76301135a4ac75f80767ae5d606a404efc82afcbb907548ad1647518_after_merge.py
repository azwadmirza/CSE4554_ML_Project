    def delete(self, name):
        '''Remove predictor'''
        ca.mindsdb_native.delete_model(name)
        return '', 200