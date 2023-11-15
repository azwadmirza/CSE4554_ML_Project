    def delete(self, name):
        '''Remove predictor'''
        g.mindsdb_native.delete_model(name)
        return '', 200