    def fit(self, Z, X=None):
        """Fit to data.

        Parameters
        ----------
        Z : pd.Series
        X : pd.DataFrame

        Returns
        -------
        self : an instance of self
        """
        z = check_series(Z, enforce_univariate=True)
        self._set_y_index(z)
        sp = check_sp(self.sp)

        # apply seasonal decomposition
        self.seasonal_ = seasonal_decompose(
            z,
            model=self.model,
            period=sp,
            filt=None,
            two_sided=True,
            extrapolate_trend=0,
        ).seasonal.iloc[:sp]

        self._is_fitted = True
        return self