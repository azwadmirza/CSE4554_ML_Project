    def __init__(self,
                 space: Optional[Union[Dict,
                                       ConfigSpace.ConfigurationSpace]] = None,
                 bohb_config: Optional[Dict] = None,
                 max_concurrent: int = 10,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None):
        from hpbandster.optimizers.config_generators.bohb import BOHB
        assert BOHB is not None, "HpBandSter must be installed!"
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."
        self._max_concurrent = max_concurrent
        self.trial_to_params = {}
        self.running = set()
        self.paused = set()
        self._metric = metric

        self._bohb_config = bohb_config

        if isinstance(space, dict) and space:
            resolved_vars, domain_vars, grid_vars = parse_spec_vars(space)
            if domain_vars or grid_vars:
                logger.warning(
                    UNRESOLVED_SEARCH_SPACE.format(
                        par="space", cls=type(self)))
                space = self.convert_search_space(space)

        self._space = space

        super(TuneBOHB, self).__init__(metric=self._metric, mode=mode)

        if self._space:
            self.setup_bohb()