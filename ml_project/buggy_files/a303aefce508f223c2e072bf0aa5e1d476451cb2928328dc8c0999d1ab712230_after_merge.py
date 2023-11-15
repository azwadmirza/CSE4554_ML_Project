    def fit(self, y, X=None, fh=None):
        """Fit to training data.

        Parameters
        ----------
        y : pd.Series
            Target time series to which to fit the forecaster.
        fh : int, list or np.array, optional (default=None)
            The forecasters horizon with the steps ahead to to predict.
        X : pd.DataFrame, optional (default=None)
            Exogenous variables are ignored
        Returns
        -------
        self : returns an instance of self.
        """
        y, _ = check_y_X(y, X)
        sp = check_sp(self.sp)
        if sp > 1 and not self.deseasonalize:
            warn("`sp` is ignored when `deseasonalise`=False")

        if self.deseasonalize:
            self.deseasonalizer_ = Deseasonalizer(sp=self.sp, model="multiplicative")
            y = self.deseasonalizer_.fit_transform(y)

        # fit exponential smoothing forecaster
        # find theta lines: Theta lines are just SES + drift
        super(ThetaForecaster, self).fit(y, fh=fh)
        self.smoothing_level_ = self._fitted_forecaster.params["smoothing_level"]

        # compute trend
        self.trend_ = self._compute_trend(y)
        self._is_fitted = True
        return self