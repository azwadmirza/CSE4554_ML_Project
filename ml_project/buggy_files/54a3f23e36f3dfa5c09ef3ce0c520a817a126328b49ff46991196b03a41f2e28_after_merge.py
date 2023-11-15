    def fit(self, X, y, sample_weight=None, weight=None):
        """Fit the model using X, y as training data.

        Parameters
        ----------
        X : array-like, shape=(n_samples,)
            Training data.

        y : array-like, shape=(n_samples,)
            Training target.

        sample_weight : array-like, shape=(n_samples,), optional, default: None
            Weights. If set to None, all weights will be set to 1 (equal
            weights).

        Returns
        -------
        self : object
            Returns an instance of self.

        Notes
        -----
        X is stored for future use, as `transform` needs X to interpolate
        new input data.
        """
        if weight is not None:
            warnings.warn("'weight' was renamed to 'sample_weight' and will "
                          "be removed in 0.16.",
                          DeprecationWarning)
            sample_weight = weight

        # Build y_
        order_inv = self._build_y(X, y, sample_weight)

        # Handle the left and right bounds on X
        self.X_min_ = np.min(self.X_)
        self.X_max_ = np.max(self.X_)

        # Build f_
        self._build_f(self.X_, self.y_)

        return self