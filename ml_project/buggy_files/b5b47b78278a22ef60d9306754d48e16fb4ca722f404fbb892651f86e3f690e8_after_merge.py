    def fit(self, X, y, sample_weight=None):
        """Fit the model according to the given training data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples in the number of samples and
            n_features is the number of features.

        y : array-like, shape (n_samples,)
            Target vector relative to X.

        sample_weight : array-like, shape (n_samples,)
            Weight given to each sample.

        Returns
        -------
        self : object
        """
        X, y = check_X_y(
            X, y, copy=False, accept_sparse=['csr'], y_numeric=True)
        if sample_weight is not None:
            sample_weight = np.array(sample_weight)
            check_consistent_length(y, sample_weight)
        else:
            sample_weight = np.ones_like(y)

        if self.epsilon < 1.0:
            raise ValueError(
                "epsilon should be greater than or equal to 1.0, got %f"
                % self.epsilon)

        if self.warm_start and hasattr(self, 'coef_'):
            parameters = np.concatenate(
                (self.coef_, [self.intercept_, self.scale_]))
        else:
            if self.fit_intercept:
                parameters = np.zeros(X.shape[1] + 2)
            else:
                parameters = np.zeros(X.shape[1] + 1)
            # Make sure to initialize the scale parameter to a strictly
            # positive value:
            parameters[-1] = 1

        # Sigma or the scale factor should be non-negative.
        # Setting it to be zero might cause undefined bounds hence we set it
        # to a value close to zero.
        bounds = np.tile([-np.inf, np.inf], (parameters.shape[0], 1))
        bounds[-1][0] = np.finfo(np.float64).eps * 10

        parameters, f, dict_ = optimize.fmin_l_bfgs_b(
            _huber_loss_and_gradient, parameters,
            args=(X, y, self.epsilon, self.alpha, sample_weight),
            maxiter=self.max_iter, pgtol=self.tol, bounds=bounds,
            iprint=0)
        if dict_['warnflag'] == 2:
            raise ValueError("HuberRegressor convergence failed:"
                             " l-BFGS-b solver terminated with %s"
                             % dict_['task'].decode('ascii'))
        # In scipy <= 1.0.0, nit may exceed maxiter.
        # See https://github.com/scipy/scipy/issues/7854.
        self.n_iter_ = min(dict_['nit'], self.max_iter)
        self.scale_ = parameters[-1]
        if self.fit_intercept:
            self.intercept_ = parameters[-2]
        else:
            self.intercept_ = 0.0
        self.coef_ = parameters[:X.shape[1]]

        residual = np.abs(
            y - safe_sparse_dot(X, self.coef_) - self.intercept_)
        self.outliers_ = residual > self.scale_ * self.epsilon
        return self