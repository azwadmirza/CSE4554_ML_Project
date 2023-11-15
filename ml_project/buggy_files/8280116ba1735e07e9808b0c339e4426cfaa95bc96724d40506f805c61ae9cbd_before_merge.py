    def fit(self, X, y=None):
        """Store all observed homology dimensions in
        :attr:`homology_dimensions_` and, for each dimension separately,
        store evenly sample filtration parameter values in :attr:`samplings_`.
        Then, return the estimator.

        This method is here to implement the usual scikit-learn API and hence
        work in pipelines.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features, 3)
            Input data. Array of persistence diagrams, each a collection of
            triples [b, d, q] representing persistent topological features
            through their birth (b), death (d) and homology dimension (q).
            It is important that, for each possible homology dimension, the
            number of triples for which q equals that homology dimension is
            constants across the entries of X.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        self : object

        """
        X = check_diagrams(X)
        validate_params(
            self.get_params(), self._hyperparameters, exclude=["n_jobs"])

        self.homology_dimensions_ = sorted(list(set(X[0, :, 2])))
        self._n_dimensions = len(self.homology_dimensions_)
        self._samplings, _ = _bin(X, metric="landscape", n_bins=self.n_bins)
        self.samplings_ = {dim: s.flatten()
                           for dim, s in self._samplings.items()}

        return self