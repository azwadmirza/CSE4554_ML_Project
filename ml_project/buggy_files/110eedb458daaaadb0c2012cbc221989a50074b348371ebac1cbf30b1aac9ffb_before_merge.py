    def load_binary_data(self, model_binary_file, encoding='utf8'):
        """Loads data from the output binary file created by FastText training"""
        with utils.smart_open(model_binary_file, 'rb') as f:
            self.load_model_params(f)
            self.load_dict(f, encoding=encoding)
            self.load_vectors(f)