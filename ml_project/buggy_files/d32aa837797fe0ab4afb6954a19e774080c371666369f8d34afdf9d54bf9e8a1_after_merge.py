    def start_params(self):
        params = np.zeros(self.k_params, dtype=np.float64)

        # A. Run a multivariate regression to get beta estimates
        endog = pd.DataFrame(self.endog.copy())
        endog = endog.interpolate()
        endog = endog.fillna(method='backfill').values
        exog = None
        if self.k_trend > 0 and self.k_exog > 0:
            exog = np.c_[self._trend_data, self.exog]
        elif self.k_trend > 0:
            exog = self._trend_data
        elif self.k_exog > 0:
            exog = self.exog

        # Although the Kalman filter can deal with missing values in endog,
        # conditional sum of squares cannot
        if np.any(np.isnan(endog)):
            mask = ~np.any(np.isnan(endog), axis=1)
            endog = endog[mask]
            if exog is not None:
                exog = exog[mask]

        # Regression and trend effects via OLS
        trend_params = np.zeros(0)
        exog_params = np.zeros(0)
        if self.k_trend > 0 or self.k_exog > 0:
            trendexog_params = np.linalg.pinv(exog).dot(endog)
            endog -= np.dot(exog, trendexog_params)
            if self.k_trend > 0:
                trend_params = trendexog_params[:self.k_trend].T
            if self.k_endog > 0:
                exog_params = trendexog_params[self.k_trend:].T

        # B. Run a VAR model on endog to get trend, AR parameters
        ar_params = []
        k_ar = self.k_ar if self.k_ar > 0 else 1
        mod_ar = var_model.VAR(endog)
        res_ar = mod_ar.fit(maxlags=k_ar, ic=None, trend='nc')
        if self.k_ar > 0:
            ar_params = np.array(res_ar.params).T.ravel()
        endog = res_ar.resid

        # Test for stationarity
        if self.k_ar > 0 and self.enforce_stationarity:
            coefficient_matrices = (
                ar_params.reshape(
                    self.k_endog * self.k_ar, self.k_endog
                ).T
            ).reshape(self.k_endog, self.k_endog, self.k_ar).T

            stationary = is_invertible([1] + list(-coefficient_matrices))

            if not stationary:
                warn('Non-stationary starting autoregressive parameters'
                     ' found. Using zeros as starting parameters.')
                ar_params *= 0

        # C. Run a VAR model on the residuals to get MA parameters
        ma_params = []
        if self.k_ma > 0:
            mod_ma = var_model.VAR(endog)
            res_ma = mod_ma.fit(maxlags=self.k_ma, ic=None, trend='nc')
            ma_params = np.array(res_ma.params.T).ravel()

            # Test for invertibility
            if self.enforce_invertibility:
                coefficient_matrices = (
                    ma_params.reshape(
                        self.k_endog * self.k_ma, self.k_endog
                    ).T
                ).reshape(self.k_endog, self.k_endog, self.k_ma).T

                invertible = is_invertible([1] + list(-coefficient_matrices))

                if not invertible:
                    warn('Non-stationary starting moving-average parameters'
                         ' found. Using zeros as starting parameters.')
                    ma_params *= 0

        # Transform trend / exog params from mean form to intercept form
        if self.k_ar > 0 and (self.k_trend > 0 or self.mle_regression):
            coefficient_matrices = (
                ar_params.reshape(
                    self.k_endog * self.k_ar, self.k_endog
                ).T
            ).reshape(self.k_endog, self.k_endog, self.k_ar).T

            tmp = np.eye(self.k_endog) - np.sum(coefficient_matrices, axis=0)

            if self.k_trend > 0:
                trend_params = np.dot(tmp, trend_params)
            if self.mle_regression > 0:
                exog_params = np.dot(tmp, exog_params)

        # 1. Intercept terms
        if self.k_trend > 0:
            params[self._params_trend] = trend_params.ravel()

        # 2. AR terms
        if self.k_ar > 0:
            params[self._params_ar] = ar_params

        # 3. MA terms
        if self.k_ma > 0:
            params[self._params_ma] = ma_params

        # 4. Regression terms
        if self.mle_regression:
            params[self._params_regression] = exog_params.ravel()

        # 5. State covariance terms
        if self.error_cov_type == 'diagonal':
            params[self._params_state_cov] = res_ar.sigma_u.diagonal()
        elif self.error_cov_type == 'unstructured':
            cov_factor = np.linalg.cholesky(res_ar.sigma_u)
            params[self._params_state_cov] = (
                cov_factor[self._idx_lower_state_cov].ravel())

        # 5. Measurement error variance terms
        if self.measurement_error:
            if self.k_ma > 0:
                params[self._params_obs_cov] = res_ma.sigma_u.diagonal()
            else:
                params[self._params_obs_cov] = res_ar.sigma_u.diagonal()

        return params