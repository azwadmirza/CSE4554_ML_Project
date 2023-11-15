    def fit(self, X, y):
        """Fit the ARDRegression model according to the given training data
        and parameters.

        Iterative procedure to maximize the evidence

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training vector, where n_samples in the number of samples and
            n_features is the number of features.
        y : array, shape = [n_samples]
            Target values (integers). Will be cast to X's dtype if necessary

        Returns
        -------
        self : returns an instance of self.
        """
        X, y = check_X_y(X, y, dtype=np.float64, y_numeric=True,
                         ensure_min_samples=2)

        n_samples, n_features = X.shape
        coef_ = np.zeros(n_features)

        X, y, X_offset_, y_offset_, X_scale_ = self._preprocess_data(
            X, y, self.fit_intercept, self.normalize, self.copy_X)

        # Launch the convergence loop
        keep_lambda = np.ones(n_features, dtype=bool)

        lambda_1 = self.lambda_1
        lambda_2 = self.lambda_2
        alpha_1 = self.alpha_1
        alpha_2 = self.alpha_2
        verbose = self.verbose

        # Initialization of the values of the parameters
        eps = np.finfo(np.float64).eps
        # Add `eps` in the denominator to omit division by zero if `np.var(y)`
        # is zero
        alpha_ = 1. / (np.var(y) + eps)
        lambda_ = np.ones(n_features)

        self.scores_ = list()
        coef_old_ = None

        # Compute sigma and mu (using Woodbury matrix identity)
        def update_sigma(X, alpha_, lambda_, keep_lambda, n_samples):
            sigma_ = pinvh(np.eye(n_samples) / alpha_ +
                           np.dot(X[:, keep_lambda] *
                           np.reshape(1. / lambda_[keep_lambda], [1, -1]),
                           X[:, keep_lambda].T))
            sigma_ = np.dot(sigma_, X[:, keep_lambda] *
                            np.reshape(1. / lambda_[keep_lambda], [1, -1]))
            sigma_ = - np.dot(np.reshape(1. / lambda_[keep_lambda], [-1, 1]) *
                              X[:, keep_lambda].T, sigma_)
            sigma_.flat[::(sigma_.shape[1] + 1)] += 1. / lambda_[keep_lambda]
            return sigma_

        def update_coeff(X, y, coef_, alpha_, keep_lambda, sigma_):
            coef_[keep_lambda] = alpha_ * np.dot(
                sigma_, np.dot(X[:, keep_lambda].T, y))
            return coef_

        # Iterative procedure of ARDRegression
        for iter_ in range(self.n_iter):
            sigma_ = update_sigma(X, alpha_, lambda_, keep_lambda, n_samples)
            coef_ = update_coeff(X, y, coef_, alpha_, keep_lambda, sigma_)

            # Update alpha and lambda
            rmse_ = np.sum((y - np.dot(X, coef_)) ** 2)
            gamma_ = 1. - lambda_[keep_lambda] * np.diag(sigma_)
            lambda_[keep_lambda] = ((gamma_ + 2. * lambda_1) /
                                    ((coef_[keep_lambda]) ** 2 +
                                     2. * lambda_2))
            alpha_ = ((n_samples - gamma_.sum() + 2. * alpha_1) /
                      (rmse_ + 2. * alpha_2))

            # Prune the weights with a precision over a threshold
            keep_lambda = lambda_ < self.threshold_lambda
            coef_[~keep_lambda] = 0

            # Compute the objective function
            if self.compute_score:
                s = (lambda_1 * np.log(lambda_) - lambda_2 * lambda_).sum()
                s += alpha_1 * log(alpha_) - alpha_2 * alpha_
                s += 0.5 * (fast_logdet(sigma_) + n_samples * log(alpha_) +
                            np.sum(np.log(lambda_)))
                s -= 0.5 * (alpha_ * rmse_ + (lambda_ * coef_ ** 2).sum())
                self.scores_.append(s)

            # Check for convergence
            if iter_ > 0 and np.sum(np.abs(coef_old_ - coef_)) < self.tol:
                if verbose:
                    print("Converged after %s iterations" % iter_)
                break
            coef_old_ = np.copy(coef_)

        # update sigma and mu using updated parameters from the last iteration
        sigma_ = update_sigma(X, alpha_, lambda_, keep_lambda, n_samples)
        coef_ = update_coeff(X, y, coef_, alpha_, keep_lambda, sigma_)

        self.coef_ = coef_
        self.alpha_ = alpha_
        self.sigma_ = sigma_
        self.lambda_ = lambda_
        self._set_intercept(X_offset_, y_offset_, X_scale_)
        return self