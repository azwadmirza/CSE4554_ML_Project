    def __init__(self,
                 space: Optional[Dict] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 utility_kwargs: Optional[Dict] = None,
                 random_state: int = 42,
                 random_search_steps: int = 10,
                 verbose: int = 0,
                 patience: int = 5,
                 skip_duplicate: bool = True,
                 analysis: Optional[ExperimentAnalysis] = None,
                 max_concurrent: Optional[int] = None,
                 use_early_stopped_trials: Optional[bool] = None):
        """Instantiate new BayesOptSearch object.

        Args:
            space (dict): Continuous search space.
                Parameters will be sampled from
                this space which will be used to run trials.
            metric (str): The training result objective value attribute.
            mode (str): One of {min, max}. Determines whether objective is
                minimizing or maximizing the metric attribute.
            utility_kwargs (dict): Parameters to define the utility function.
                Must provide values for the keys `kind`, `kappa`, and `xi`.
            random_state (int): Used to initialize BayesOpt.
            random_search_steps (int): Number of initial random searches.
                This is necessary to avoid initial local overfitting
                of the Bayesian process.
            patience (int): Must be > 0. If the optimizer suggests a set of
                hyperparameters more than 'patience' times,
                then the whole experiment will stop.
            skip_duplicate (bool): If true, BayesOptSearch will not create
                a trial with a previously seen set of hyperparameters. By
                default, floating values will be reduced to a digit precision
                of 5. You can override this by setting
                ``searcher.repeat_float_precision``.
            analysis (ExperimentAnalysis): Optionally, the previous analysis
                to integrate.
            verbose (int): Sets verbosity level for BayesOpt packages.
            max_concurrent: Deprecated.
            use_early_stopped_trials: Deprecated.
        """
        assert byo is not None, (
            "BayesOpt must be installed!. You can install BayesOpt with"
            " the command: `pip install bayesian-optimization`.")
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."
        self.max_concurrent = max_concurrent
        self._config_counter = defaultdict(int)
        self._patience = patience
        # int: Precision at which to hash values.
        self.repeat_float_precision = 5
        if self._patience <= 0:
            raise ValueError("patience must be set to a value greater than 0!")
        self._skip_duplicate = skip_duplicate
        super(BayesOptSearch, self).__init__(
            metric=metric,
            mode=mode,
            max_concurrent=max_concurrent,
            use_early_stopped_trials=use_early_stopped_trials)

        if utility_kwargs is None:
            # The defaults arguments are the same
            # as in the package BayesianOptimization
            utility_kwargs = dict(
                kind="ucb",
                kappa=2.576,
                xi=0.0,
            )

        if mode == "max":
            self._metric_op = 1.
        elif mode == "min":
            self._metric_op = -1.

        self._live_trial_mapping = {}
        self._buffered_trial_results = []
        self.random_search_trials = random_search_steps
        self._total_random_search_trials = 0

        self.utility = byo.UtilityFunction(**utility_kwargs)

        # Registering the provided analysis, if given
        if analysis is not None:
            self.register_analysis(analysis)

        self._space = space
        self._verbose = verbose
        self._random_state = random_state

        self.optimizer = None
        if space:
            self.setup_optimizer()