    def predict_proba(self, X, batch_size=None, n_jobs=1):
        return self._automl.predict(X, batch_size=batch_size, n_jobs=n_jobs)