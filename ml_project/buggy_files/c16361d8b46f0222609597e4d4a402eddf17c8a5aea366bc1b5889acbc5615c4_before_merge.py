    def transform(self, X, y=None):
        """Compute multi-channel raster images from diagrams in `X` by
        convolution with a Gaussian kernel.

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
        Xt : ndarray of shape (n_samples, n_homology_dimensions, n_bins, \
             n_bins)
            Multi-channel raster images: one image per sample and one channel
            per homology dimension seen in :meth:`fit`. Index i along axis 1
            corresponds to the i-th homology dimension in
            :attr:`homology_dimensions_`.

        """
        check_is_fitted(self)
        X = check_diagrams(X, copy=True)

        Xt = Parallel(n_jobs=self.n_jobs, mmap_mode="c")(
            delayed(persistence_images)(
                _subdiagrams(X[s], [dim], remove_dim=True),
                self._samplings[dim],
                self._step_size[dim],
                self.weights_[dim],
                self.sigma
                )
            for dim in self.homology_dimensions_
            for s in gen_even_slices(len(X), effective_n_jobs(self.n_jobs))
            )
        Xt = np.concatenate(Xt).\
            reshape(self._n_dimensions, len(X), self.n_bins, self.n_bins).\
            transpose((1, 0, 2, 3))
        return Xt