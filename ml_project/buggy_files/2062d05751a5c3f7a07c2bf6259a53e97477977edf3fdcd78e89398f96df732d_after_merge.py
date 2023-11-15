    def transform(self, X, y=None):
        """Compute the persistence landscapes of diagrams in `X`.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features, 3)
            Input data. Array of persistence diagrams, each a collection of
            triples [b, d, q] representing persistent topological features
            through their birth (b), death (d) and homology dimension (q).

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        Xt : ndarray of shape (n_samples, n_homology_dimensions, \
            n_layers, n_bins)
            Persistence lanscapes: one landscape (represented as a
            two-dimensional array) per sample and per homology dimension seen
            in :meth:`fit`. Each landscape contains a number `n_layers` of
            layers. Index i along axis 1 corresponds to the i-th homology
            dimension in :attr:`homology_dimensions_`.

        """
        check_is_fitted(self)
        X = check_diagrams(X)

        Xt = Parallel(n_jobs=self.n_jobs)(delayed(landscapes)(
                _subdiagrams(X[s], [dim], remove_dim=True),
                self._samplings[dim],
                self.n_layers)
            for dim in self.homology_dimensions_
            for s in gen_even_slices(len(X), effective_n_jobs(self.n_jobs)))
        Xt = np.concatenate(Xt).\
            reshape(self._n_dimensions, len(X), self.n_layers, self.n_bins).\
            transpose((1, 0, 2, 3))
        return Xt