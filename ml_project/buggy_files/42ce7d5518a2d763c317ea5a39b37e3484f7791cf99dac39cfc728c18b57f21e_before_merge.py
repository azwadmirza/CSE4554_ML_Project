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
        # input checks
        if X is not None:
            raise NotImplementedError()

        # set values
        self._set_y_X(y, X)
        self._set_fh(fh)

        self.step_length_ = check_step_length(self.step_length)
        self.window_length_ = check_window_length(self.window_length)

        # set up cv iterator, for recursive strategy, a single estimator
        # is fit for a one-step-ahead forecasting horizon and then called
        # iteratively to predict multiple steps ahead
        self._cv = SlidingWindowSplitter(
            fh=1,
            window_length=self.window_length_,
            step_length=self.step_length_,
            start_with_window=True,
        )

        # transform data into tabular form
        X_train_tab, y_train_tab = self._transform(y, X)

        # fit base regressor
        regressor = clone(self.regressor)
        regressor.fit(X_train_tab, y_train_tab.ravel())
        self.regressor_ = regressor

        self._is_fitted = True
        return self