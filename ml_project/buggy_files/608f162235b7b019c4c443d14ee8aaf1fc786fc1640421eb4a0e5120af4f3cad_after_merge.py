    def __init__(
            self,
            space: Optional[Dict] = None,
            metric: Optional[str] = None,
            mode: Optional[str] = None,
            points_to_evaluate: Optional[List[Dict]] = None,
            n_initial_points: int = 20,
            random_state_seed: Optional[int] = None,
            gamma: float = 0.25,
            max_concurrent: Optional[int] = None,
            use_early_stopped_trials: Optional[bool] = None,
    ):
        assert hpo is not None, (
            "HyperOpt must be installed! Run `pip install hyperopt`.")
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."
        from hyperopt.fmin import generate_trials_to_calculate
        super(HyperOptSearch, self).__init__(
            metric=metric,
            mode=mode,
            max_concurrent=max_concurrent,
            use_early_stopped_trials=use_early_stopped_trials)
        self.max_concurrent = max_concurrent
        # hyperopt internally minimizes, so "max" => -1
        if mode == "max":
            self.metric_op = -1.
        elif mode == "min":
            self.metric_op = 1.

        if n_initial_points is None:
            self.algo = hpo.tpe.suggest
        else:
            self.algo = partial(
                hpo.tpe.suggest, n_startup_jobs=n_initial_points)
        if gamma is not None:
            self.algo = partial(self.algo, gamma=gamma)
        if points_to_evaluate is None:
            self._hpopt_trials = hpo.Trials()
            self._points_to_evaluate = 0
        else:
            assert isinstance(points_to_evaluate, (list, tuple))
            self._hpopt_trials = generate_trials_to_calculate(
                points_to_evaluate)
            self._hpopt_trials.refresh()
            self._points_to_evaluate = len(points_to_evaluate)
        self._live_trial_mapping = {}
        if random_state_seed is None:
            self.rstate = np.random.RandomState()
        else:
            self.rstate = np.random.RandomState(random_state_seed)

        self.domain = None
        if isinstance(space, dict) and space:
            resolved_vars, domain_vars, grid_vars = parse_spec_vars(space)
            if domain_vars or grid_vars:
                logger.warning(
                    UNRESOLVED_SEARCH_SPACE.format(
                        par="space", cls=type(self)))
                space = self.convert_search_space(space)
            self.domain = hpo.Domain(lambda spc: spc, space)