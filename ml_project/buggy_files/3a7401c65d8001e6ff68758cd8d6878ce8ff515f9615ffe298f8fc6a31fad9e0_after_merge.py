    def fit(self, X, y, n_jobs=1):
        """
        Fit linear model.

        Parameters
        ----------
        X : numpy array or sparse matrix of shape [n_samples,n_features]
            Training data
        y : numpy array of shape [n_samples, n_targets]
            Target values

        Returns
        -------
        self : returns an instance of self.
        """
        if n_jobs != 1:
            warnings.warn("The n_jobs parameter in fit is deprecated and will "
                          "be removed in 0.17. It has been moved from the fit "
                          "method to the LinearRegression class constructor.",
                          DeprecationWarning, stacklevel=2)
            n_jobs_ = n_jobs
        else:
            n_jobs_ = self.n_jobs
        X = check_array(X, accept_sparse=['csr', 'csc', 'coo'])
        y = np.asarray(y)

        X, y, X_mean, y_mean, X_std = self._center_data(
            X, y, self.fit_intercept, self.normalize, self.copy_X)

        if sp.issparse(X):
            if y.ndim < 2:
                out = sparse_lsqr(X, y)
                self.coef_ = out[0]
                self.residues_ = out[3]
            else:
                # sparse_lstsq cannot handle y with shape (M, K)
                outs = Parallel(n_jobs=n_jobs_)(
                    delayed(sparse_lsqr)(X, y[:, j].ravel())
                    for j in range(y.shape[1]))
                self.coef_ = np.vstack(out[0] for out in outs)
                self.residues_ = np.vstack(out[3] for out in outs)
        else:
            self.coef_, self.residues_, self.rank_, self.singular_ = \
                linalg.lstsq(X, y)
            self.coef_ = self.coef_.T

        if y.ndim == 1:
            self.coef_ = np.ravel(self.coef_)
        self._set_intercept(X_mean, y_mean, X_std)
        return self