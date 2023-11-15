    def __init__(self, configspace, **kwargs):
        _gp_searcher = kwargs.get('_gp_searcher')
        if _gp_searcher is None:
            kwargs['configspace'] = configspace
            _kwargs = check_and_merge_defaults(
                kwargs, *gp_fifo_searcher_defaults(),
                dict_name='search_options')
            _gp_searcher = gp_fifo_searcher_factory(**_kwargs)
        super().__init__(
            _gp_searcher.hp_ranges.config_space,
            reward_attribute=kwargs.get('reward_attribute'))
        self.gp_searcher = _gp_searcher
        # This lock protects gp_searcher. We are not using self.LOCK, this
        # can lead to deadlocks when superclass methods are called
        self._gp_lock = mp.Lock()