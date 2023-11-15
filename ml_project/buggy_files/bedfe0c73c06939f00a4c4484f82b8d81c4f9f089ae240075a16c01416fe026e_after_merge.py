    def preproces(self, data):
        if self.normalize:
            if sp.issparse(data.X):
                self.Warning.no_sparse_normalization()
            else:
                data = Normalize()(data)
        for preprocessor in KMeans.preprocessors:  # use same preprocessors than
            data = preprocessor(data)
        return data