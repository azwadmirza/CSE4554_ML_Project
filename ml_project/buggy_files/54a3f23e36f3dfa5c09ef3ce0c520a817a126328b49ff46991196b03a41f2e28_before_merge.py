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

        X, y, sample_weight = check_arrays(X, y, sample_weight,
                                           sparse_format='dense')
        y = as_float_array(y)
        self._check_fit_data(X, y, sample_weight)

        # Determine increasing if auto-determination requested
        if self.increasing == 'auto':
            self.increasing_ = check_increasing(X, y)
        else:
            self.increasing_ = self.increasing

        order = np.argsort(X)
        self.X_ = as_float_array(X[order], copy=False)
        self.y_ = isotonic_regression(y[order], sample_weight, self.y_min,
                                      self.y_max, increasing=self.increasing_)

        # Handle the left and right bounds on X
        self.X_min_ = np.min(self.X_)
        self.X_max_ = np.max(self.X_)

        return self