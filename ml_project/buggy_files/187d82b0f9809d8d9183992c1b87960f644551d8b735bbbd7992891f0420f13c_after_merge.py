    def fit(self, maxlag=None, method='cmle', ic=None, trend='c',
            transparams=True, start_params=None, solver=None, maxiter=35,
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
        start_params : array-like, optional
            A first guess on the parameters.  Default is cmle estimates.
        solver : str or None, optional
            Solver to be used.  The default is 'l_bfgs' (limited memory Broyden-
            Fletcher-Goldfarb-Shanno).  Other choices are 'bfgs', 'newton'
            (Newton-Raphson), 'nm' (Nelder-Mead), 'cg' - (conjugate gradient),
            'ncg' (non-conjugate gradient), and 'powell'.
            The limited memory BFGS uses m=30 to approximate the Hessian,
            projected gradient tolerance of 1e-7 and factr = 1e3.  These
            cannot currently be changed for l_bfgs.  See notes for more
            information.
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

        See also
        --------
        statsmodels.base.model.LikelihoodModel.fit : for more information on using
            the solvers.

        """
        method = method.lower()
        if method not in ['cmle','yw','mle']:
            raise ValueError("Method %s not recognized" % method)
        self.method = method
        self.trend = trend
        self.transparams = transparams
        nobs = len(self.endog) # overwritten if method is 'cmle'
        endog = self.endog

        if maxlag is None:
            maxlag = int(round(12*(nobs/100.)**(1/4.)))
        k_ar = maxlag # stays this if ic is None

        # select lag length
        if ic is not None:
            ic = ic.lower()
            if ic not in ['aic','bic','hqic','t-stat']:
                raise ValueError("ic option %s not understood" % ic)
            k_ar = self.select_order(k_ar, ic, trend, method)

        self.k_ar = k_ar # change to what was chosen by ic

        # redo estimation for best lag
        # make LHS
        Y = endog[k_ar:,:]
        # make lagged RHS
        X = self._stackX(k_ar, trend) # sets self.k_trend
        k_trend = self.k_trend
        k = k_trend
        self.exog_names = util.make_lag_names(self.endog_names, k_ar, k_trend)
        self.Y = Y
        self.X = X

        if solver:
            solver = solver.lower()
        if method == "cmle":     # do OLS
            arfit = OLS(Y,X).fit()
            params = arfit.params
            self.nobs = nobs - k_ar
            self.sigma2 = arfit.ssr/arfit.nobs #needed for predict fcasterr
        if method == "mle":
            self.nobs = nobs
            if start_params is None:
                start_params = OLS(Y,X).fit().params
            else:
                if len(start_params) != k_trend + k_ar:
                    raise ValueError("Length of start params is %d. There"
                            " are %d parameters." % (len(start_params),
                                                     k_trend + k_ar))
            start_params = self._invtransparams(start_params)
            loglike = lambda params : -self.loglike(params)
            if solver == None:  # use limited memory bfgs
                bounds = [(None,)*2]*(k_ar+k)
                mlefit = optimize.fmin_l_bfgs_b(loglike, start_params,
                    approx_grad=True, m=12, pgtol=1e-8, factr=1e2,
                    bounds=bounds, iprint=disp)
                self.mlefit = mlefit
                params = mlefit[0]
            else:
                mlefit = super(AR, self).fit(start_params=start_params,
                            method=solver, maxiter=maxiter,
                            full_output=full_output, disp=disp,
                            callback = callback, **kwargs)
                self.mlefit = mlefit
                params = mlefit.params
            if self.transparams:
                params = self._transparams(params)
                self.transparams = False # turn off now for other results

        # don't use yw, because we can't estimate the constant
        #elif method == "yw":
        #    params, omega = yule_walker(endog, order=maxlag,
        #            method="mle", demean=False)
           # how to handle inference after Yule-Walker?
        #    self.params = params #TODO: don't attach here
        #    self.omega = omega

        pinv_exog = np.linalg.pinv(X)
        normalized_cov_params = np.dot(pinv_exog, pinv_exog.T)
        arfit = ARResults(self, params, normalized_cov_params)
        return ARResultsWrapper(arfit)