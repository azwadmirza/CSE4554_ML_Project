    def __init__(self,
                 optimizer: Optional[sko.optimizer.Optimizer] = None,
                 space: Union[List[str], Dict[str, Union[Tuple, List]]] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 points_to_evaluate: Optional[List[List]] = None,
                 evaluated_rewards: Optional[List] = None,
                 max_concurrent: Optional[int] = None,
                 use_early_stopped_trials: Optional[bool] = None):
        assert sko is not None, """skopt must be installed!
            You can install Skopt with the command:
            `pip install scikit-optimize`."""

        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."
        self.max_concurrent = max_concurrent
        super(SkOptSearch, self).__init__(
            metric=metric,
            mode=mode,
            max_concurrent=max_concurrent,
            use_early_stopped_trials=use_early_stopped_trials)

        self._initial_points = []
        self._parameters = None
        self._parameter_names = None
        self._parameter_ranges = None

        self._space = space

        if self._space:
            if isinstance(optimizer, sko.Optimizer):
                if not isinstance(space, list):
                    raise ValueError(
                        "You passed an optimizer instance to SkOpt. Your "
                        "`space` parameter should be a list of parameter"
                        "names.")
                self._parameter_names = space
            else:
                self._parameter_names = list(space.keys())
                self._parameter_ranges = space.values()

        self._points_to_evaluate = points_to_evaluate
        self._evaluated_rewards = evaluated_rewards

        self._skopt_opt = optimizer
        if self._skopt_opt or self._space:
            self.setup_skopt()

        self._live_trial_mapping = {}