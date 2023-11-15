    def _fit_start_params_hr(self, order, start_ar_lags=None):
        """
        Get starting parameters for fit.

        Parameters
        ----------
        order : iterable
            (p,q,k) - AR lags, MA lags, and number of exogenous variables
            including the constant.
        start_ar_lags : int, optional
            If start_ar_lags is not None, rather than fitting an AR process
            according to best BIC, fits an AR process with a lag length equal
            to start_ar_lags.

        Returns
        -------
        start_params : array
            A first guess at the starting parameters.

        Notes
        -----
        If necessary, fits an AR process with the laglength start_ar_lags, or
        selected according to best BIC if start_ar_lags is None.  Obtain the
        residuals.  Then fit an ARMA(p,q) model via OLS using these residuals
        for a first approximation.  Uses a separate OLS regression to find the
        coefficients of exogenous variables.

        References
        ----------
        Hannan, E.J. and Rissanen, J.  1982.  "Recursive estimation of mixed
            autoregressive-moving average order."  `Biometrika`.  69.1.

        Durbin, J. 1960. "The Fitting of Time-Series Models."
        `Review of the International Statistical Institute`. Vol. 28, No. 3
        """
        p, q, k = order
        start_params = zeros((p+q+k))
        # make copy of endog because overwritten
        endog = np.array(self.endog, np.float64)
        exog = self.exog
        if k != 0:
            ols_params = OLS(endog, exog).fit().params
            start_params[:k] = ols_params
            endog -= np.dot(exog, ols_params).squeeze()
        if q != 0:
            if p != 0:
                # make sure we don't run into small data problems in AR fit
                nobs = len(endog)
                if start_ar_lags is None:
                    maxlag = int(round(12*(nobs/100.)**(1/4.)))
                    if maxlag >= nobs:
                        maxlag = nobs - 1
                    armod = AR(endog).fit(ic='bic', trend='nc', maxlag=maxlag)
                else:
                    if start_ar_lags >= nobs:
                        start_ar_lags = nobs - 1
                    armod = AR(endog).fit(trend='nc', maxlag=start_ar_lags)
                arcoefs_tmp = armod.params
                p_tmp = armod.k_ar
                # it's possible in small samples that optimal lag-order
                # doesn't leave enough obs. No consistent way to fix.
                if p_tmp + q >= len(endog):
                    raise ValueError("Proper starting parameters cannot"
                                     " be found for this order with this "
                                     "number of observations. Use the "
                                     "start_params argument, or set "
                                     "start_ar_lags to an integer less than "
                                     "len(endog) - q.")
                resid = endog[p_tmp:] - np.dot(lagmat(endog, p_tmp,
                                                      trim='both'),
                                               arcoefs_tmp)
                if p < p_tmp + q:
                    endog_start = p_tmp + q - p
                    resid_start = 0
                else:
                    endog_start = 0
                    resid_start = p - p_tmp - q
                lag_endog = lagmat(endog, p, 'both')[endog_start:]
                lag_resid = lagmat(resid, q, 'both')[resid_start:]
                # stack ar lags and resids
                X = np.column_stack((lag_endog, lag_resid))
                coefs = OLS(endog[max(p_tmp + q, p):], X).fit().params
                start_params[k:k+p+q] = coefs
            else:
                start_params[k+p:k+p+q] = yule_walker(endog, order=q)[0]
        if q == 0 and p != 0:
            arcoefs = yule_walker(endog, order=p)[0]
            start_params[k:k+p] = arcoefs

        # check AR coefficients
        if p and not np.all(np.abs(np.roots(np.r_[1, -start_params[k:k + p]]
                                            )) < 1):
            raise ValueError("The computed initial AR coefficients are not "
                             "stationary\nYou should induce stationarity, "
                             "choose a different model order, or you can\n"
                             "pass your own start_params.")
        # check MA coefficients
        elif q and not np.all(np.abs(np.roots(np.r_[1, start_params[k + p:]]
                                              )) < 1):
            raise ValueError("The computed initial MA coefficients are not "
                             "invertible\nYou should induce invertibility, "
                             "choose a different model order, or you can\n"
                             "pass your own start_params.")

        # check MA coefficients
        return start_params