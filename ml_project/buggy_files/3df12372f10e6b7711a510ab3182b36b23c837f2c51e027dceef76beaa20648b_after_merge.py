    def __init__(
        self,
        error="add",
        trend=None,
        damped=False,
        seasonal=None,
        sp=1,
        initialization_method="estimated",
        initial_level=None,
        initial_trend=None,
        initial_seasonal=None,
        bounds=None,
        dates=None,
        freq=None,
        missing="none",
        start_params=None,
        maxiter=1000,
        full_output=True,
        disp=False,
        callback=None,
        return_params=False,
        auto=False,
        information_criterion="aic",
        allow_multiplicative_trend=False,
        restrict=True,
        additive_only=False,
        n_jobs=None,
        **kwargs
    ):

        # Model params
        self.error = error
        self.trend = trend
        self.damped = damped
        self.seasonal = seasonal
        self.sp = sp
        self.initialization_method = initialization_method
        self.initial_level = initial_level
        self.initial_trend = initial_trend
        self.initial_seasonal = initial_seasonal
        self.bounds = bounds
        self.dates = dates
        self.freq = freq
        self.missing = missing

        # Fit params
        self.start_params = start_params
        self.maxiter = maxiter
        self.full_output = full_output
        self.disp = disp
        self.callback = callback
        self.return_params = return_params
        self.information_criterion = information_criterion
        self.auto = auto
        self.allow_multiplicative_trend = allow_multiplicative_trend
        self.restrict = restrict
        self.additive_only = additive_only
        self.n_jobs = n_jobs

        super(AutoETS, self).__init__()