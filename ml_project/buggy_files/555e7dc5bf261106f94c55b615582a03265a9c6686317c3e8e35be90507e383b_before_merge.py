    def __init__(self, endog, exog=None, order=(1, 0, 0),
                 seasonal_order=(0, 0, 0, 0), trend=None,
                 measurement_error=False, time_varying_regression=False,
                 mle_regression=True, simple_differencing=False,
                 enforce_stationarity=True, enforce_invertibility=True,
                 hamilton_representation=False, concentrate_scale=False,
                 trend_offset=1, use_exact_diffuse=False, **kwargs):

        # Save given orders
        self.order = order
        self.seasonal_order = seasonal_order

        # Validate orders
        if len(self.order) != 3:
            raise ValueError('`order` argument must be an iterable with three'
                             ' elements.')
        if len(self.seasonal_order) != 4:
            raise ValueError('`seasonal_order` argument must be an iterable'
                             ' with four elements.')

        # Model parameters
        self.seasonal_periods = seasonal_order[3]
        self.measurement_error = measurement_error
        self.time_varying_regression = time_varying_regression
        self.mle_regression = mle_regression
        self.simple_differencing = simple_differencing
        self.enforce_stationarity = enforce_stationarity
        self.enforce_invertibility = enforce_invertibility
        self.hamilton_representation = hamilton_representation
        self.concentrate_scale = concentrate_scale
        self.use_exact_diffuse = use_exact_diffuse

        # Enforce non-MLE coefficients if time varying coefficients is
        # specified
        if self.time_varying_regression and self.mle_regression:
            raise ValueError('Models with time-varying regression coefficients'
                             ' must integrate the coefficients as part of the'
                             ' state vector, so that `mle_regression` must'
                             ' be set to False.')

        # Lag polynomials
        # Assume that they are given from lowest degree to highest, that all
        # degrees except for the constant are included, and that they are
        # boolean vectors (0 for not included, 1 for included).
        if isinstance(order[0], (int, np.integer)):
            self.polynomial_ar = np.r_[1., np.ones(order[0])]
        else:
            self.polynomial_ar = np.r_[1., order[0]]
        self._polynomial_ar = self.polynomial_ar.copy()
        if isinstance(order[2], (int, np.integer)):
            self.polynomial_ma = np.r_[1., np.ones(order[2])]
        else:
            self.polynomial_ma = np.r_[1., order[2]]
        self._polynomial_ma = self.polynomial_ma.copy()
        # Assume that they are given from lowest degree to highest, that the
        # degrees correspond to (1*s, 2*s, ..., P*s), and that they are
        # boolean vectors (0 for not included, 1 for included).
        if isinstance(seasonal_order[0], (int, np.integer)):
            self.polynomial_seasonal_ar = np.r_[
                1.,  # constant
                ([0] * (self.seasonal_periods - 1) + [1]) * seasonal_order[0]
            ]
        else:
            self.polynomial_seasonal_ar = np.r_[
                1., [0] * self.seasonal_periods * len(seasonal_order[0])
            ]
            for i in range(len(seasonal_order[0])):
                tmp = (i + 1) * self.seasonal_periods
                self.polynomial_seasonal_ar[tmp] = seasonal_order[0][i]
        self._polynomial_seasonal_ar = self.polynomial_seasonal_ar.copy()
        if isinstance(seasonal_order[2], (int, np.integer)):
            self.polynomial_seasonal_ma = np.r_[
                1.,  # constant
                ([0] * (self.seasonal_periods - 1) + [1]) * seasonal_order[2]
            ]
        else:
            self.polynomial_seasonal_ma = np.r_[
                1., [0] * self.seasonal_periods * len(seasonal_order[2])
            ]
            for i in range(len(seasonal_order[2])):
                tmp = (i + 1) * self.seasonal_periods
                self.polynomial_seasonal_ma[tmp] = seasonal_order[2][i]
        self._polynomial_seasonal_ma = self.polynomial_seasonal_ma.copy()

        # Deterministic trend polynomial
        self.trend = trend
        self.trend_offset = trend_offset
        self.polynomial_trend, self.k_trend = prepare_trend_spec(self.trend)
        self._polynomial_trend = self.polynomial_trend.copy()

        # Model orders
        # Note: k_ar, k_ma, k_seasonal_ar, k_seasonal_ma do not include the
        # constant term, so they may be zero.
        # Note: for a typical ARMA(p,q) model, p = k_ar_params = k_ar - 1 and
        # q = k_ma_params = k_ma - 1, although this may not be true for models
        # with arbitrary log polynomials.
        self.k_ar = int(self.polynomial_ar.shape[0] - 1)
        self.k_ar_params = int(np.sum(self.polynomial_ar) - 1)
        self.k_diff = int(order[1])
        self.k_ma = int(self.polynomial_ma.shape[0] - 1)
        self.k_ma_params = int(np.sum(self.polynomial_ma) - 1)

        self.k_seasonal_ar = int(self.polynomial_seasonal_ar.shape[0] - 1)
        self.k_seasonal_ar_params = (
            int(np.sum(self.polynomial_seasonal_ar) - 1)
        )
        self.k_seasonal_diff = int(seasonal_order[1])
        self.k_seasonal_ma = int(self.polynomial_seasonal_ma.shape[0] - 1)
        self.k_seasonal_ma_params = (
            int(np.sum(self.polynomial_seasonal_ma) - 1)
        )

        # Make sure we don't have a seasonal specification without a valid
        # seasonal period.
        if self.seasonal_order[3] == 1:
            raise ValueError('Seasonal period must be greater than 1.')
        if self.seasonal_order[3] == 0 and (self.k_seasonal_ar > 0 or
                                            self.k_seasonal_ma > 0):
            raise ValueError('Seasonal AR or MA components cannot be set when'
                             ' the given seasonal period is equal to 0.')

        # Make internal copies of the differencing orders because if we use
        # simple differencing, then we will need to internally use zeros after
        # the simple differencing has been performed
        self._k_diff = self.k_diff
        self._k_seasonal_diff = self.k_seasonal_diff

        # We can only use the Hamilton representation if differencing is not
        # performed as a part of the state space
        if (self.hamilton_representation and not (self.simple_differencing or
           self._k_diff == self._k_seasonal_diff == 0)):
            raise ValueError('The Hamilton representation is only available'
                             ' for models in which there is no differencing'
                             ' integrated into the state vector. Set'
                             ' `simple_differencing` to True or set'
                             ' `hamilton_representation` to False')

        # Model order
        # (this is used internally in a number of locations)
        self._k_order = max(self.k_ar + self.k_seasonal_ar,
                            self.k_ma + self.k_seasonal_ma + 1)
        if self._k_order == 1 and self.k_ar + self.k_seasonal_ar == 0:
            # Handle time-varying regression
            if self.time_varying_regression:
                self._k_order = 0

        # Exogenous data
        (self.k_exog, exog) = prepare_exog(exog)

        # Redefine mle_regression to be true only if it was previously set to
        # true and there are exogenous regressors
        self.mle_regression = (
            self.mle_regression and exog is not None and self.k_exog > 0
        )
        # State regression is regression with coefficients estimated within
        # the state vector
        self.state_regression = (
            not self.mle_regression and exog is not None and self.k_exog > 0
        )
        # If all we have is a regression (so k_ar = k_ma = 0), then put the
        # error term as measurement error
        if self.state_regression and self._k_order == 0:
            self.measurement_error = True

        # Number of states
        k_states = self._k_order
        if not self.simple_differencing:
            k_states += (self.seasonal_periods * self._k_seasonal_diff +
                         self._k_diff)
        if self.state_regression:
            k_states += self.k_exog

        # Number of positive definite elements of the state covariance matrix
        k_posdef = int(self._k_order > 0)
        # Only have an error component to the states if k_posdef > 0
        self.state_error = k_posdef > 0
        if self.state_regression and self.time_varying_regression:
            k_posdef += self.k_exog

        # Diffuse initialization can be more sensistive to the variance value
        # in the case of state regression, so set a higher than usual default
        # variance
        if self.state_regression:
            kwargs.setdefault('initial_variance', 1e10)

        # Handle non-default loglikelihood burn
        self._loglikelihood_burn = kwargs.get('loglikelihood_burn', None)

        # Number of parameters
        self.k_params = (
            self.k_ar_params + self.k_ma_params +
            self.k_seasonal_ar_params + self.k_seasonal_ma_params +
            self.k_trend +
            self.measurement_error +
            int(not self.concentrate_scale)
        )
        if self.mle_regression:
            self.k_params += self.k_exog

        # We need to have an array or pandas at this point
        self.orig_endog = endog
        self.orig_exog = exog
        if not _is_using_pandas(endog, None):
            endog = np.asanyarray(endog)

        # Update the differencing dimensions if simple differencing is applied
        self.orig_k_diff = self._k_diff
        self.orig_k_seasonal_diff = self._k_seasonal_diff
        if (self.simple_differencing and
           (self._k_diff > 0 or self._k_seasonal_diff > 0)):
            self._k_diff = 0
            self._k_seasonal_diff = 0

        # Internally used in several locations
        self._k_states_diff = (
            self._k_diff + self.seasonal_periods * self._k_seasonal_diff
        )

        # Set some model variables now so they will be available for the
        # initialize() method, below
        self.nobs = len(endog)
        self.k_states = k_states
        self.k_posdef = k_posdef

        # Initialize the statespace
        super(SARIMAX, self).__init__(
            endog, exog=exog, k_states=k_states, k_posdef=k_posdef, **kwargs
        )

        # Set the filter to concentrate out the scale if requested
        if self.concentrate_scale:
            self.ssm.filter_concentrated = True

        # Set as time-varying model if we have time-trend or exog
        if self.k_exog > 0 or len(self.polynomial_trend) > 1:
            self.ssm._time_invariant = False

        # Initialize the fixed components of the statespace model
        self.ssm['design'] = self.initial_design
        self.ssm['state_intercept'] = self.initial_state_intercept
        self.ssm['transition'] = self.initial_transition
        self.ssm['selection'] = self.initial_selection
        if self.concentrate_scale:
            self.ssm['state_cov', 0, 0] = 1.

        # update _init_keys attached by super
        self._init_keys += ['order', 'seasonal_order', 'trend',
                            'measurement_error', 'time_varying_regression',
                            'mle_regression', 'simple_differencing',
                            'enforce_stationarity', 'enforce_invertibility',
                            'hamilton_representation', 'concentrate_scale',
                            'trend_offset'] + list(kwargs.keys())
        # TODO: I think the kwargs or not attached, need to recover from ???

        # Initialize the state
        if self.ssm.initialization is None:
            self.initialize_default()