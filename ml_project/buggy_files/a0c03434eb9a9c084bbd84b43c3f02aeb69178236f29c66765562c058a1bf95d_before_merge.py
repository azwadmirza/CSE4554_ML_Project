    def __init__(self,
                 space: Optional[List[Dict]] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 parameter_constraints: Optional[List] = None,
                 outcome_constraints: Optional[List] = None,
                 ax_client: Optional[AxClient] = None,
                 use_early_stopped_trials: Optional[bool] = None,
                 max_concurrent: Optional[int] = None):
        assert ax is not None, "Ax must be installed!"
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."

        super(AxSearch, self).__init__(
            metric=metric,
            mode=mode,
            max_concurrent=max_concurrent,
            use_early_stopped_trials=use_early_stopped_trials)

        self._ax = ax_client
        self._space = space
        self._parameter_constraints = parameter_constraints
        self._outcome_constraints = outcome_constraints

        self.max_concurrent = max_concurrent

        self._objective_name = metric
        self._parameters = []
        self._live_trial_mapping = {}

        if self._ax or self._space:
            self.setup_experiment()