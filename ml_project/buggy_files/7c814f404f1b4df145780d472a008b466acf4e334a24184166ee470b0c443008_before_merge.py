    def __init__(self, endog=None, exog=None, order=None,
                 seasonal_order=None, ar_order=None, diff=None, ma_order=None,
                 seasonal_ar_order=None, seasonal_diff=None,
                 seasonal_ma_order=None, seasonal_periods=None, trend=None,
                 enforce_stationarity=None, enforce_invertibility=None,
                 concentrate_scale=None, dates=None, freq=None,
                 missing='none'):

        # Basic parameters
        self.enforce_stationarity = enforce_stationarity
        self.enforce_invertibility = enforce_invertibility
        self.concentrate_scale = concentrate_scale

        # Validate that we were not given conflicting specifications
        has_order = order is not None
        has_specific_order = (ar_order is not None or diff is not None or
                              ma_order is not None)
        has_seasonal_order = seasonal_order is not None
        has_specific_seasonal_order = (seasonal_ar_order is not None or
                                       seasonal_diff is not None or
                                       seasonal_ma_order is not None or
                                       seasonal_periods is not None)
        if has_order and has_specific_order:
            raise ValueError('Cannot specify both `order` and either of'
                             ' `ar_order` or `ma_order`.')
        if has_seasonal_order and has_specific_seasonal_order:
            raise ValueError('Cannot specify both `seasonal_order` and any of'
                             ' `seasonal_ar_order`, `seasonal_ma_order`,'
                             ' or `seasonal_periods`.')

        # Compute `order`
        if has_specific_order:
            ar_order = 0 if ar_order is None else ar_order
            diff = 0 if diff is None else diff
            ma_order = 0 if ma_order is None else ma_order
            order = (ar_order, diff, ma_order)
        elif not has_order:
            order = (0, 0, 0)

        # Compute `seasonal_order`
        if has_specific_seasonal_order:
            seasonal_ar_order = (
                0 if seasonal_ar_order is None else seasonal_ar_order)
            seasonal_diff = 0 if seasonal_diff is None else seasonal_diff
            seasonal_ma_order = (
                0 if seasonal_ma_order is None else seasonal_ma_order)
            seasonal_periods = (
                0 if seasonal_periods is None else seasonal_periods)
            seasonal_order = (seasonal_ar_order, seasonal_diff,
                              seasonal_ma_order, seasonal_periods)
        elif not has_seasonal_order:
            seasonal_order = (0, 0, 0, 0)

        # Validate differencing parameters
        if order[1] < 0:
            raise ValueError('Cannot specify negative differencing.')
        if order[1] != int(order[1]):
            raise ValueError('Cannot specify fractional differencing.')
        if seasonal_order[1] < 0:
            raise ValueError('Cannot specify negative seasonal differencing.')
        if seasonal_order[1] != int(seasonal_order[1]):
            raise ValueError('Cannot specify fractional seasonal'
                             ' differencing.')
        if seasonal_order[3] < 0:
            raise ValueError('Cannot specify negative seasonal periodicity.')

        # Standardize to integers or lists of integers
        order = (
            standardize_lag_order(order[0], 'AR'),
            int(order[1]),
            standardize_lag_order(order[2], 'MA'))
        seasonal_order = (
            standardize_lag_order(seasonal_order[0], 'seasonal AR'),
            int(seasonal_order[1]),
            standardize_lag_order(seasonal_order[2], 'seasonal MA'),
            int(seasonal_order[3]))

        # Validate seasonals
        if ((seasonal_order[0] != 0 or seasonal_order[1] != 0 or
                seasonal_order[2] != 0) and seasonal_order[3] == 0):
            raise ValueError('Must include nonzero seasonal periodicity if'
                             ' including seasonal AR, MA, or differencing.')

        # Basic order
        self.order = order
        self.ar_order, self.diff, self.ma_order = order

        self.seasonal_order = seasonal_order
        (self.seasonal_ar_order, self.seasonal_diff, self.seasonal_ma_order,
         self.seasonal_periods) = seasonal_order

        # Lists of included lags
        if isinstance(self.ar_order, list):
            self.ar_lags = self.ar_order
        else:
            self.ar_lags = np.arange(1, self.ar_order + 1).tolist()
        if isinstance(self.ma_order, list):
            self.ma_lags = self.ma_order
        else:
            self.ma_lags = np.arange(1, self.ma_order + 1).tolist()

        if isinstance(self.seasonal_ar_order, list):
            self.seasonal_ar_lags = self.seasonal_ar_order
        else:
            self.seasonal_ar_lags = (
                np.arange(1, self.seasonal_ar_order + 1).tolist())
        if isinstance(self.seasonal_ma_order, list):
            self.seasonal_ma_lags = self.seasonal_ma_order
        else:
            self.seasonal_ma_lags = (
                np.arange(1, self.seasonal_ma_order + 1).tolist())

        # Maximum lag orders
        self.max_ar_order = self.ar_lags[-1] if self.ar_lags else 0
        self.max_ma_order = self.ma_lags[-1] if self.ma_lags else 0

        self.max_seasonal_ar_order = (
            self.seasonal_ar_lags[-1] if self.seasonal_ar_lags else 0)
        self.max_seasonal_ma_order = (
            self.seasonal_ma_lags[-1] if self.seasonal_ma_lags else 0)

        self.max_reduced_ar_order = (
            self.max_ar_order +
            self.max_seasonal_ar_order * self.seasonal_periods)
        self.max_reduced_ma_order = (
            self.max_ma_order +
            self.max_seasonal_ma_order * self.seasonal_periods)

        # Check that we don't have duplicate AR or MA lags from the seasonal
        # component
        ar_lags = set(self.ar_lags)
        seasonal_ar_lags = set(np.array(self.seasonal_ar_lags)
                               * self.seasonal_periods)
        duplicate_ar_lags = ar_lags.intersection(seasonal_ar_lags)
        if len(duplicate_ar_lags) > 0:
            raise ValueError('Invalid model: autoregressive lag(s) %s are'
                             ' in both the seasonal and non-seasonal'
                             ' autoregressive components.'
                             % duplicate_ar_lags)

        ma_lags = set(self.ma_lags)
        seasonal_ma_lags = set(np.array(self.seasonal_ma_lags)
                               * self.seasonal_periods)
        duplicate_ma_lags = ma_lags.intersection(seasonal_ma_lags)
        if len(duplicate_ma_lags) > 0:
            raise ValueError('Invalid model: moving average lag(s) %s are'
                             ' in both the seasonal and non-seasonal'
                             ' moving average components.'
                             % duplicate_ma_lags)

        # Handle trend
        self.trend_poly, _ = prepare_trend_spec(trend)
        # This contains the included exponents of the trend polynomial,
        # where e.g. the constant term has exponent 0, a linear trend has
        # exponent 1, etc.
        self.trend_terms = np.where(self.trend_poly == 1)[0]
        # Trend order is either the degree of the trend polynomial, if all
        # exponents are included, or a list of included exponents. Here we need
        # to make a distinction between a degree zero polynomial (i.e. a
        # constant) and the zero polynomial (i.e. not even a constant). The
        # former has `trend_order = 0`, while the latter has
        # `trend_order = None`.
        if len(self.trend_terms) == 0:
            self.trend_order = None
            self.trend_degree = None
        elif np.all(self.trend_terms == np.arange(len(self.trend_terms))):
            self.trend_order = self.trend_terms[-1]
            self.trend_degree = self.trend_terms[-1]
        else:
            self.trend_order = self.trend_terms
            self.trend_degree = self.trend_terms[-1]

        # Handle endog / exog
        # Standardize exog
        _, exog = prepare_exog(exog)

        # Standardize endog (including creating a faux endog if necessary)
        faux_endog = endog is None
        if endog is None:
            endog = [] if exog is None else np.zeros(len(exog)) * np.nan

        # Add trend data into exog
        nobs = len(endog) if exog is None else len(exog)
        if self.trend_order is not None:
            trend_data = self.construct_trend_data(nobs)
            if exog is None:
                exog = trend_data
            elif _is_using_pandas(exog, None):
                trend_data = pd.DataFrame(trend_data, index=exog.index,
                                          columns=self.construct_trend_names())
                exog = pd.concat([trend_data, exog], axis=1)
            else:
                exog = np.c_[trend_data, exog]

        # Create an underlying time series model, to handle endog / exog,
        # especially validating shapes, retrieving names, and potentially
        # providing us with a time series index
        self._model = TimeSeriesModel(endog, exog=exog, dates=dates, freq=freq,
                                      missing=missing)
        self.endog = None if faux_endog else self._model.endog
        self.exog = self._model.exog

        self._has_missing = (
            None if faux_endog else np.any(np.isnan(self.endog)))