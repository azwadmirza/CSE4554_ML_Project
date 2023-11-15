    def _predict(self, X):
        """Collect results from clf.predict calls."""
        return np.asarray([clf.predict(X) for clf in self.clfs_]).T