    def start_params(self):
        params = np.zeros(self.k_params, dtype=np.float64)

        endog = self.endog.copy()

        # 1. Factor loadings (estimated via PCA)
        if self.k_factors > 0:
            # Use principal components + OLS as starting values
            res_pca = PCA(endog, ncomp=self.k_factors)
            mod_ols = OLS(endog, res_pca.factors)
            res_ols = mod_ols.fit()

            # Using OLS params for the loadings tends to gives higher starting
            # log-likelihood.
            params[self._params_loadings] = res_ols.params.T.ravel()
            # params[self._params_loadings] = res_pca.loadings.ravel()

            # However, using res_ols.resid tends to causes non-invertible
            # starting VAR coefficients for error VARs
            # endog = res_ols.resid
            endog = endog - np.dot(res_pca.factors, res_pca.loadings.T)

        # 2. Exog (OLS on residuals)
        if self.k_exog > 0:
            mod_ols = OLS(endog, exog=self.exog)
            res_ols = mod_ols.fit()
            # In the form: beta.x1.y1, beta.x2.y1, beta.x1.y2, ...
            params[self._params_exog] = res_ols.params.T.ravel()
            endog = res_ols.resid

        # 3. Factors (VAR on res_pca.factors)
        stationary = True
        if self.k_factors > 1 and self.factor_order > 0:
            # 3a. VAR transition (OLS on factors estimated via PCA)
            mod_factors = VAR(res_pca.factors)
            res_factors = mod_factors.fit(maxlags=self.factor_order, ic=None,
                                          trend='nc')
            # Save the parameters
            params[self._params_factor_transition] = (
                res_factors.params.T.ravel())

            # Test for stationarity
            coefficient_matrices = (
                params[self._params_factor_transition].reshape(
                    self.k_factors * self.factor_order, self.k_factors
                ).T
            ).reshape(self.k_factors, self.k_factors, self.factor_order).T

            stationary = is_invertible([1] + list(-coefficient_matrices))
        elif self.k_factors > 0 and self.factor_order > 0:
            # 3b. AR transition
            Y = res_pca.factors[self.factor_order:]
            X = lagmat(res_pca.factors, self.factor_order, trim='both')
            params_ar = np.linalg.pinv(X).dot(Y)
            stationary = is_invertible(np.r_[1, -params_ar.squeeze()])
            params[self._params_factor_transition] = params_ar[:, 0]

        # Check for stationarity
        if not stationary and self.enforce_stationarity:
            raise ValueError('Non-stationary starting autoregressive'
                             ' parameters found with `enforce_stationarity`'
                             ' set to True.')

        # 4. Errors
        if self.error_order == 0:
            if self.error_cov_type == 'scalar':
                params[self._params_error_cov] = endog.var(axis=0).mean()
            elif self.error_cov_type == 'diagonal':
                params[self._params_error_cov] = endog.var(axis=0)
            elif self.error_cov_type == 'unstructured':
                cov_factor = np.diag(endog.std(axis=0))
                params[self._params_error_cov] = (
                    cov_factor[self._idx_lower_error_cov].ravel())
        else:
            mod_errors = VAR(endog)
            res_errors = mod_errors.fit(maxlags=self.error_order, ic=None,
                                        trend='nc')

            # Test for stationarity
            coefficient_matrices = (
                np.array(res_errors.params.T).ravel().reshape(
                    self.k_endog * self.error_order, self.k_endog
                ).T
            ).reshape(self.k_endog, self.k_endog, self.error_order).T

            stationary = is_invertible([1] + list(-coefficient_matrices))
            if not stationary and self.enforce_stationarity:
                raise ValueError('Non-stationary starting error autoregressive'
                                 ' parameters found with'
                                 ' `enforce_stationarity` set to True.')

            # Get the error autoregressive parameters
            if self.error_var:
                params[self._params_error_transition] = (
                    np.array(res_errors.params.T).ravel())
            else:
                # In the case of individual autoregressions, extract just the
                # diagonal elements
                # TODO: can lead to explosive parameterizations
                params[self._params_error_transition] = (
                    res_errors.params.T[self._idx_error_diag])

            # Get the error covariance parameters
            if self.error_cov_type == 'scalar':
                params[self._params_error_cov] = (
                    res_errors.sigma_u.diagonal().mean())
            elif self.error_cov_type == 'diagonal':
                params[self._params_error_cov] = res_errors.sigma_u.diagonal()
            elif self.error_cov_type == 'unstructured':
                try:
                    cov_factor = np.linalg.cholesky(res_errors.sigma_u)
                except np.linalg.LinAlgError:
                    cov_factor = np.eye(res_errors.sigma_u.shape[0]) * (
                        res_errors.sigma_u.diagonal().mean()**0.5)
                cov_factor = np.eye(res_errors.sigma_u.shape[0]) * (
                    res_errors.sigma_u.diagonal().mean()**0.5)
                params[self._params_error_cov] = (
                    cov_factor[self._idx_lower_error_cov].ravel())

        return params