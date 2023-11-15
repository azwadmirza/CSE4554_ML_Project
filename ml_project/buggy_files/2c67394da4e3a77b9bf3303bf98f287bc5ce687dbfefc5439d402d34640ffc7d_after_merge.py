    def __init__(self, endog, exog=None, order=(0, 0, 0),
                 seasonal_order=(0, 0, 0, 0), trend=None,
                 enforce_stationarity=True, enforce_invertibility=True,
                 concentrate_scale=False, dates=None, freq=None,
                 missing='none'):
        # Default for trend
        # 'c' if there is no integration and 'n' otherwise
        # TODO: if trend='c', then we could alternatively use `demean=True` in
        # the estimation methods rather than setting up `exog` and using GLS.
        # Not sure if it's worth the trouble though.
        integrated = order[1] > 0 or seasonal_order[1] > 0
        if trend is None and not integrated:
            trend = 'c'
        elif trend is None:
            trend = 'n'

        # Construct the specification
        # (don't pass specific values of enforce stationarity/invertibility,
        # because we don't actually want to restrict the estimators based on
        # this criteria. Instead, we'll just make sure that the parameter
        # estimates from those methods satisfy the criteria.)
        self._spec_arima = SARIMAXSpecification(
            endog, exog=exog, order=order, seasonal_order=seasonal_order,
            trend=trend, enforce_stationarity=None, enforce_invertibility=None,
            concentrate_scale=concentrate_scale, dates=dates, freq=freq,
            missing=missing)
        exog = self._spec_arima._model.data.orig_exog

        # Initialize the base SARIMAX class
        # Note: we don't pass in a trend value to the base class, since ARIMA
        # standardizes the trend to always be part of exog, while the base
        # SARIMAX class puts it in the transition equation.
        super(ARIMA, self).__init__(
            endog, exog, order=order, seasonal_order=seasonal_order,
            enforce_stationarity=enforce_stationarity,
            enforce_invertibility=enforce_invertibility,
            concentrate_scale=concentrate_scale, dates=dates, freq=freq,
            missing=missing)