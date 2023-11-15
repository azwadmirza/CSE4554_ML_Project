    def preprocess(self, X):
        X = super().preprocess(X).fillna(0)
        return X