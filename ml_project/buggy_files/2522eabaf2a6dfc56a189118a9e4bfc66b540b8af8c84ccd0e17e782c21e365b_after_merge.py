    def _fit_forecaster(self, y, X=None):

        # Select model automatically
        if self.auto:
            # Initialise parameter ranges
            error_range = ["add", "mul"]
            if self.allow_multiplicative_trend:
                trend_range = ["add", "mul", None]
            else:
                trend_range = ["add", None]
            if self.sp <= 1 or self.sp is None:
                seasonal_range = [None]
            else:
                seasonal_range = ["add", "mul", None]
            damped_range = [True, False]

            # Check information criterion input
            if (
                self.information_criterion != "aic"
                and self.information_criterion != "bic"
                and self.information_criterion != "aicc"
            ):
                raise ValueError(
                    "information criterion must " "either be aic, bic or aicc"
                )

            # Fit model, adapted from:
            # https://github.com/robjhyndman/forecast/blob/master/R/ets.R

            # Initialise iterator
            def _iter(error_range, trend_range, seasonal_range, damped_range):
                for error, trend, seasonal, damped in product(
                    error_range, trend_range, seasonal_range, damped_range
                ):
                    if trend is None and damped:
                        continue

                    if self.restrict:
                        if error == "add" and (trend == "mul" or seasonal == "mul"):
                            continue
                        if error == "mul" and trend == "mul" and seasonal == "add":
                            continue
                        if self.additive_only and (
                            error == "mul" or trend == "mul" or seasonal == "mul"
                        ):
                            continue

                    yield error, trend, seasonal, damped

            # Fit function
            def _fit(error, trend, seasonal, damped):
                _forecaster = _ETSModel(
                    y,
                    error=error,
                    trend=trend,
                    damped_trend=damped,
                    seasonal=seasonal,
                    seasonal_periods=self.sp,
                    initialization_method=self.initialization_method,
                    initial_level=self.initial_level,
                    initial_trend=self.initial_trend,
                    initial_seasonal=self.initial_seasonal,
                    bounds=self.bounds,
                    dates=self.dates,
                    freq=self.freq,
                    missing=self.missing,
                )
                _fitted_forecaster = _forecaster.fit(
                    start_params=self.start_params,
                    maxiter=self.maxiter,
                    full_output=self.full_output,
                    disp=self.disp,
                    callback=self.callback,
                    return_params=self.return_params,
                )
                return _forecaster, _fitted_forecaster

            # Fit models
            _fitted_results = Parallel(n_jobs=self.n_jobs)(
                delayed(_fit)(error, trend, seasonal, damped)
                for error, trend, seasonal, damped in _iter(
                    error_range, trend_range, seasonal_range, damped_range
                )
            )

            # Select best model based on information criterion
            # Get index of best model
            _index = np.argmin(
                [
                    getattr(result[1], self.information_criterion)
                    for result in _fitted_results
                ]
            )
            # Update best model
            self._forecaster = _fitted_results[_index][0]
            self._fitted_forecaster = _fitted_results[_index][1]

        else:
            self._forecaster = _ETSModel(
                y,
                error=self.error,
                trend=self.trend,
                damped_trend=self.damped,
                seasonal=self.seasonal,
                seasonal_periods=self.sp,
                initialization_method=self.initialization_method,
                initial_level=self.initial_level,
                initial_trend=self.initial_trend,
                initial_seasonal=self.initial_seasonal,
                bounds=self.bounds,
                dates=self.dates,
                freq=self.freq,
                missing=self.missing,
            )

            self._fitted_forecaster = self._forecaster.fit(
                start_params=self.start_params,
                maxiter=self.maxiter,
                full_output=self.full_output,
                disp=self.disp,
                callback=self.callback,
                return_params=self.return_params,
            )