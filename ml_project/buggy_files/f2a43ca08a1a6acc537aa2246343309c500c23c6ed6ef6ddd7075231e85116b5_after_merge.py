    def get(self, name):
        '''Export predictor to file'''
        try:
            new_name = request.args.get('new_name')
            ca.mindsdb_native.rename_model(name, new_name)
        except Exception as e:
            return str(e), 400

        return f'Renamed model to {new_name}', 200