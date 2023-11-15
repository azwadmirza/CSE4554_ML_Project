    def _predict(self, X):
        """Collect results from clf.predict calls."""

        if self.refit:
            return np.asarray([clf.predict(X) for clf in self.clfs_]).T
        else:
            return np.asarray([self.le_.transform(clf.predict(X))
                               for clf in self.clfs_]).T