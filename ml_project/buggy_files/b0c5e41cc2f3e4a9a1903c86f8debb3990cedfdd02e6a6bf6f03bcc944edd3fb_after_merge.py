    def fit(self, maxlag=None, method='cmle', ic=None, trend='c',
            transparams=True, start_params=None, solver='lbfgs', maxiter=35,
            full_output=1, disp=1, callback=None, **kwargs):
        """
        Fit the unconditional maximum likelihood of an AR(p) process.

        Parameters
        ----------
        maxlag : int
            If `ic` is None, then maxlag is the lag length used in fit.  If
            `ic` is specified then maxlag is the highest lag order used to
            select the correct lag order.  If maxlag is None, the default is
            round(12*(nobs/100.)**(1/4.))
        method : str {'cmle', 'mle'}, optional
            cmle - Conditional maximum likelihood using OLS
            mle - Unconditional (exact) maximum likelihood.  See `solver`
            and the Notes.
        ic : str {'aic','bic','hic','t-stat'}
            Criterion used for selecting the optimal lag length.
            aic - Akaike Information Criterion
            bic - Bayes Information Criterion
            t-stat - Based on last lag
            hqic - Hannan-Quinn Information Criterion
            If any of the information criteria are selected, the lag length
            which results in the lowest value is selected.  If t-stat, the
            model starts with maxlag and drops a lag until the highest lag
            has a t-stat that is significant at the 95 % level.
        trend : str {'c','nc'}
            Whether to include a constant or not. 'c' - include constant.
            'nc' - no constant.

        The below can be specified if method is 'mle'

        transparams : bool, optional
            Whether or not to transform the parameters to ensure stationarity.
            Uses the transformation suggested in Jones (1980).
        start_params : array_like, optional
            A first guess on the parameters.  Default is cmle estimates.
        solver : str or None, optional
            Solver to be used if method is 'mle'.  The default is 'lbfgs'
            (limited memory Broyden-Fletcher-Goldfarb-Shanno).  Other choices
            are 'bfgs', 'newton' (Newton-Raphson), 'nm' (Nelder-Mead),
            'cg' - (conjugate gradient), 'ncg' (non-conjugate gradient),
            and 'powell'.
        maxiter : int, optional
            The maximum number of function evaluations. Default is 35.
        tol : float
            The convergence tolerance.  Default is 1e-08.
        full_output : bool, optional
            If True, all output from solver will be available in
            the Results object's mle_retvals attribute.  Output is dependent
            on the solver.  See Notes for more information.
        disp : bool, optional
            If True, convergence information is output.
        callback : function, optional
            Called after each iteration as callback(xk) where xk is the current
            parameter vector.
        kwargs
            See Notes for keyword arguments that can be passed to fit.

        References
        ----------
        Jones, R.H. 1980 "Maximum likelihood fitting of ARMA models to time
            series with missing observations."  `Technometrics`.  22.3.
            389-95.

        See Also
        --------
        statsmodels.base.model.LikelihoodModel.fit
        """
        start_params = array_like(start_params, 'start_params', ndim=1,
                                  optional=True)
        method = method.lower()
        if method not in ['cmle', 'mle']:
            raise ValueError("Method %s not recognized" % method)
        self.method = method
        self.trend = trend
        self.transparams = transparams
        nobs = len(self.endog)  # overwritten if method is 'cmle'
        endog = self.endog
        # The parameters are no longer allowed to change in an instance
        fit_params = (maxlag, method, ic, trend)
        if self._fit_params is not None and self._fit_params != fit_params:
            raise RuntimeError(REPEATED_FIT_ERROR.format(*self._fit_params))
        if maxlag is None:
            maxlag = int(round(12 * (nobs / 100.) ** (1 / 4.)))
        k_ar = maxlag  # stays this if ic is None

        # select lag length
        if ic is not None:
            ic = ic.lower()
            if ic not in ['aic', 'bic', 'hqic', 't-stat']:
                raise ValueError("ic option %s not understood" % ic)
            k_ar = self.select_order(k_ar, ic, trend, method)

        self.k_ar = k_ar  # change to what was chosen by ic

        # redo estimation for best lag
        # make LHS
        Y = endog[k_ar:, :]
        # make lagged RHS
        X = self._stackX(k_ar, trend)  # sets self.k_trend
        k_trend = self.k_trend
        self.exog_names = util.make_lag_names(self.endog_names, k_ar, k_trend)
        self.Y = Y
        self.X = X

        if method == "cmle":  # do OLS
            arfit = OLS(Y, X).fit()
            params = arfit.params
            self.nobs = nobs - k_ar
            self.sigma2 = arfit.ssr / arfit.nobs  # needed for predict fcasterr

        else:  # method == "mle"
            solver = solver.lower()
            self.nobs = nobs
            if start_params is None:
                start_params = OLS(Y, X).fit().params
            else:
                if len(start_params) != k_trend + k_ar:
                    raise ValueError("Length of start params is %d. There"
                                     " are %d parameters." %
                                     (len(start_params), k_trend + k_ar))
            start_params = self._invtransparams(start_params)
            if solver == 'lbfgs':
                kwargs.setdefault('pgtol', 1e-8)
                kwargs.setdefault('factr', 1e2)
                kwargs.setdefault('m', 12)
                kwargs.setdefault('approx_grad', True)
            mlefit = super(AR, self).fit(start_params=start_params,
                                         method=solver, maxiter=maxiter,
                                         full_output=full_output, disp=disp,
                                         callback=callback, **kwargs)

            params = mlefit.params
            if self.transparams:
                params = self._transparams(params)
                self.transparams = False  # turn off now for other results

        pinv_exog = np.linalg.pinv(X)
        normalized_cov_params = np.dot(pinv_exog, pinv_exog.T)
        arfit = ARResults(copy.copy(self), params, normalized_cov_params)
        if method == 'mle' and full_output:
            arfit.mle_retvals = mlefit.mle_retvals
            arfit.mle_settings = mlefit.mle_settings
        # Set fit params since completed the fit
        if self._fit_params is None:
            self._fit_params = fit_params
        return ARResultsWrapper(arfit)