    def __init__(self,
                 space: Optional[ConfigSpace.ConfigurationSpace] = None,
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
        self._space = space

        super(TuneBOHB, self).__init__(metric=self._metric, mode=mode)

        if self._space:
            self.setup_bohb()