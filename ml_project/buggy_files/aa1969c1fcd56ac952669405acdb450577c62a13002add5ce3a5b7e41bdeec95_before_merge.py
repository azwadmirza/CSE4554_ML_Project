    def preprocess(self, X):
        X = convert_categorical_to_int(X)
        return super().preprocess(X)