    def __init__(self,
                 optimizer: Optional[BlackboxOptimiser] = None,
                 domain: Optional[str] = None,
                 space: Optional[Union[Dict, List[Dict]]] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 points_to_evaluate: Optional[List[List]] = None,
                 evaluated_rewards: Optional[List] = None,
                 **kwargs):
        assert dragonfly is not None, """dragonfly must be installed!
            You can install Dragonfly with the command:
            `pip install dragonfly-opt`."""
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."

        super(DragonflySearch, self).__init__(
            metric=metric, mode=mode, **kwargs)

        self._opt_arg = optimizer
        self._domain = domain

        if isinstance(space, dict) and space:
            resolved_vars, domain_vars, grid_vars = parse_spec_vars(space)
            if domain_vars or grid_vars:
                logger.warning(
                    UNRESOLVED_SEARCH_SPACE.format(
                        par="space", cls=type(self)))
                space = self.convert_search_space(space)

        self._space = space
        self._points_to_evaluate = points_to_evaluate
        self._evaluated_rewards = evaluated_rewards
        self._initial_points = []
        self._live_trial_mapping = {}

        self._opt = None
        if isinstance(optimizer, BlackboxOptimiser):
            if domain or space:
                raise ValueError(
                    "If you pass an optimizer instance to dragonfly, do not "
                    "pass a `domain` or `space`.")
            self._opt = optimizer
            self.init_dragonfly()
        elif self._space:
            self.setup_dragonfly()