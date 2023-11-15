    def fit(self, X, y):
        """Fit MultiTaskLasso model with coordinate descent

        Parameters
        -----------
        X: ndarray, shape = (n_samples, n_features)
            Data
        y: ndarray, shape = (n_samples, n_tasks)
            Target

        Notes
        -----

        Coordinate descent is an algorithm that considers each column of
        data at a time hence it will automatically convert the X input
        as a Fortran-contiguous numpy array if necessary.

        To avoid memory re-allocation it is advised to allocate the
        initial data in memory directly using that format.
        """
        # X and y must be of type float64
        X = array2d(X, dtype=np.float64, order='F',
                    copy=self.copy_X and self.fit_intercept)
        y = np.asarray(y, dtype=np.float64)

        if hasattr(self, 'l1_ratio'):
            model_str = 'ElasticNet'
        else:
            model_str = 'Lasso'
        if y.ndim == 1:
            raise ValueError("For mono-task outputs, use %s" % model_str)

        n_samples, n_features = X.shape
        _, n_tasks = y.shape

        X, y, X_mean, y_mean, X_std = center_data(
            X, y, self.fit_intercept, self.normalize, copy=False)

        if not self.warm_start or self.coef_ is None:
            self.coef_ = np.zeros((n_tasks, n_features), dtype=np.float64,
                                  order='F')

        l1_reg = self.alpha * self.l1_ratio * n_samples
        l2_reg = self.alpha * (1.0 - self.l1_ratio) * n_samples

        self.coef_ = np.asfortranarray(self.coef_)  # coef contiguous in memory

        self.coef_, self.dual_gap_, self.eps_ = \
            cd_fast.enet_coordinate_descent_multi_task(
                self.coef_, l1_reg, l2_reg, X, y, self.max_iter, self.tol)

        self._set_intercept(X_mean, y_mean, X_std)

        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want'
                          ' to increase the number of iterations')

        # return self for chaining fit and predict calls
        return self