    def fit(self, start_params=None, trend='c', method="css-mle",
            transparams=True, solver='lbfgs', maxiter=500, full_output=1,
            disp=5, callback=None, start_ar_lags=None, **kwargs):
        """
        Fits ARMA(p,q) model using exact maximum likelihood via Kalman filter.

        Parameters
        ----------
        start_params : array_like, optional
            Starting parameters for ARMA(p,q). If None, the default is given
            by ARMA._fit_start_params.  See there for more information.
        transparams : bool, optional
            Whether or not to transform the parameters to ensure stationarity.
            Uses the transformation suggested in Jones (1980).  If False,
            no checking for stationarity or invertibility is done.
        method : str {'css-mle','mle','css'}
            This is the loglikelihood to maximize.  If "css-mle", the
            conditional sum of squares likelihood is maximized and its values
            are used as starting values for the computation of the exact
            likelihood via the Kalman filter.  If "mle", the exact likelihood
            is maximized via the Kalman Filter.  If "css" the conditional sum
            of squares likelihood is maximized.  All three methods use
            `start_params` as starting parameters.  See above for more
            information.
        trend : str {'c','nc'}
            Whether to include a constant or not.  'c' includes constant,
            'nc' no constant.
        solver : str or None, optional
            Solver to be used.  The default is 'lbfgs' (limited memory
            Broyden-Fletcher-Goldfarb-Shanno).  Other choices are 'bfgs',
            'newton' (Newton-Raphson), 'nm' (Nelder-Mead), 'cg' -
            (conjugate gradient), 'ncg' (non-conjugate gradient), and
            'powell'. By default, the limited memory BFGS uses m=12 to
            approximate the Hessian, projected gradient tolerance of 1e-8 and
            factr = 1e2. You can change these by using kwargs.
        maxiter : int, optional
            The maximum number of function evaluations. Default is 500.
        tol : float
            The convergence tolerance.  Default is 1e-08.
        full_output : bool, optional
            If True, all output from solver will be available in
            the Results object's mle_retvals attribute.  Output is dependent
            on the solver.  See Notes for more information.
        disp : int, optional
            If True, convergence information is printed.  For the default
            l_bfgs_b solver, disp controls the frequency of the output during
            the iterations. disp < 0 means no output in this case.
        callback : function, optional
            Called after each iteration as callback(xk) where xk is the current
            parameter vector.
        start_ar_lags : int, optional
            Parameter for fitting start_params. When fitting start_params,
            residuals are obtained from an AR fit, then an ARMA(p,q) model is
            fit via OLS using these residuals. If start_ar_lags is None, fit
            an AR process according to best BIC. If start_ar_lags is not None,
            fits an AR process with a lag length equal to start_ar_lags.
            See ARMA._fit_start_params_hr for more information.
        kwargs
            See Notes for keyword arguments that can be passed to fit.

        Returns
        -------
        statsmodels.tsa.arima_model.ARMAResults class

        See Also
        --------
        statsmodels.base.model.LikelihoodModel.fit : for more information
            on using the solvers.
        ARMAResults : results class returned by fit

        Notes
        -----
        If fit by 'mle', it is assumed for the Kalman Filter that the initial
        unknown state is zero, and that the initial variance is
        P = dot(inv(identity(m**2)-kron(T,T)),dot(R,R.T).ravel('F')).reshape(r,
        r, order = 'F')

        """
        if self._fit_params is not None:
            fp = (trend, method)
            if self._fit_params != fp:
                raise RuntimeError(REPEATED_FIT_ERROR.format(*fp, mod='ARMA'))

        k_ar = self.k_ar
        k_ma = self.k_ma

        # enforce invertibility
        self.transparams = transparams

        endog, exog = self.endog, self.exog
        k_exog = self.k_exog
        self.nobs = len(endog)  # this is overwritten if method is 'css'

        # (re)set trend and handle exogenous variables
        # always pass original exog

        if hasattr(self, 'k_trend'):
            k_trend = self.k_trend
            exog = self.exog
        else:
            # Ensures only call once per ARMA instance
            k_trend, exog = _make_arma_exog(endog, self.exog, trend)

        # Check has something to estimate
        if k_ar == 0 and k_ma == 0 and k_trend == 0 and k_exog == 0:
            raise ValueError("Estimation requires the inclusion of least one "
                             "AR term, MA term, a constant or an exogenous "
                             "variable.")

        # check again now that we know the trend
        _check_estimable(len(endog), k_ar + k_ma + k_exog + k_trend)

        self.k_trend = k_trend
        self.exog = exog  # overwrites original exog from __init__

        # (re)set names for this model
        self.exog_names = _make_arma_names(self.data, k_trend,
                                           (k_ar, k_ma), self._orig_exog_names)
        k = k_trend + k_exog

        # choose objective function
        if k_ma == 0 and k_ar == 0:
            method = "css"  # Always CSS when no AR or MA terms

        self.method = method = method.lower()

        # adjust nobs for css
        if method == 'css':
            self.nobs = len(self.endog) - k_ar

        if start_params is not None:
            start_params = array_like(start_params, 'start_params')
        else:  # estimate starting parameters
            start_params = self._fit_start_params((k_ar, k_ma, k), method,
                                                  start_ar_lags)

        if transparams:  # transform initial parameters to ensure invertibility
            start_params = self._invtransparams(start_params)

        if solver == 'lbfgs':
            kwargs.setdefault('pgtol', 1e-8)
            kwargs.setdefault('factr', 1e2)
            kwargs.setdefault('m', 12)
            kwargs.setdefault('approx_grad', True)
        mlefit = super(ARMA, self).fit(start_params, method=solver,
                                       maxiter=maxiter,
                                       full_output=full_output, disp=disp,
                                       callback=callback, **kwargs)
        params = mlefit.params

        if transparams:  # transform parameters back
            params = self._transparams(params)

        self.transparams = False  # so methods do not expect transf.

        normalized_cov_params = None  # TODO: fix this
        armafit = ARMAResults(copy.copy(self), params, normalized_cov_params)
        armafit.mle_retvals = mlefit.mle_retvals
        armafit.mle_settings = mlefit.mle_settings
        # Save core fit parameters for future checks
        self._fit_params = (trend, method)

        return ARMAResultsWrapper(armafit)