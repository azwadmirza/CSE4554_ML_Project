    def fit(self, X, y=None):
        """Store relevant homology dimensions in
        :attr:`homology_dimensions_`. Then, return the estimator.

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
            constants across the entries of `X`.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        self : object

        """
        X = check_diagrams(X)
        validate_params(
            self.get_params(), self._hyperparameters)

        if self.homology_dimensions is None:
            # Find the unique homology dimensions in the 3D array X passed to
            # `fit` assuming that they can all be found in its zero-th entry
            homology_dimensions = np.unique(X[0, :, 2])
        else:
            homology_dimensions = self.homology_dimensions
        self.homology_dimensions_ = \
            _homology_dimensions_to_sorted_ints(homology_dimensions)

        return self