    def fit(self, y, X=None, fh=None):
        """Fit to training data.

        Parameters
        ----------
        y : pd.Series
            Target time series to which to fit the forecaster.
        fh : int, list or np.array, optional (default=None)
            The forecasters horizon with the steps ahead to to predict.
        X : pd.DataFrame, optional (default=None)
            Exogenous variables (ignored)

        Returns
        -------
        self : returns an instance of self.
        """
        y, X = check_y_X(y, X)
        self._set_y_X(y, X)
        self._set_fh(fh)

        self._forecaster = self._instantiate_model()
        self._forecaster = self._forecaster.fit(y)

        self._is_fitted = True
        return self