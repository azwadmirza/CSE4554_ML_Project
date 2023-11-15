    def post(self):
        '''Upload existing predictor'''
        predictor_file = request.files['file']
        # @TODO: Figure out how to remove
        fpath = os.path.join(mindsdb.CONFIG.MINDSDB_TEMP_PATH, 'new.zip')
        with open(fpath, 'wb') as f:
            f.write(predictor_file.read())

        ca.mindsdb_native.load_model(fpath)
        try:
            os.remove(fpath)
        except Exception:
            pass

        return '', 200