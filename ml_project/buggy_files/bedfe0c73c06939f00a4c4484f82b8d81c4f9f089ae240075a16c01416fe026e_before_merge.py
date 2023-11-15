    def preproces(self, data):
        if self.normalize:
            data = Normalize()(data)
        for preprocessor in KMeans.preprocessors:  # use same preprocessors than
            data = preprocessor(data)
        return data