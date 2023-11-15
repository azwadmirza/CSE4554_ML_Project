    def __init__(self,
                 algo: str = "asracos",
                 budget: Optional[int] = None,
                 dim_dict: Optional[Dict] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 **kwargs):
        assert zoopt is not None, "ZOOpt not found - please install zoopt " \
                                  "by `pip install -U zoopt`."
        assert budget is not None, "`budget` should not be None!"
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."
        _algo = algo.lower()
        assert _algo in ["asracos", "sracos"
                         ], "`algo` must be in ['asracos', 'sracos'] currently"

        self._algo = _algo

        if isinstance(dim_dict, dict) and dim_dict:
            resolved_vars, domain_vars, grid_vars = parse_spec_vars(dim_dict)
            if domain_vars or grid_vars:
                logger.warning(
                    UNRESOLVED_SEARCH_SPACE.format(
                        par="dim_dict", cls=type(self)))
                dim_dict = self.convert_search_space(dim_dict, join=True)

        self._dim_dict = dim_dict
        self._budget = budget

        self._metric = metric
        if mode == "max":
            self._metric_op = -1.
        elif mode == "min":
            self._metric_op = 1.
        self._live_trial_mapping = {}

        self._dim_keys = []
        self.solution_dict = {}
        self.best_solution_list = []
        self.optimizer = None

        self.kwargs = kwargs

        super(ZOOptSearch, self).__init__(metric=self._metric, mode=mode)

        if self._dim_dict:
            self.setup_zoopt()