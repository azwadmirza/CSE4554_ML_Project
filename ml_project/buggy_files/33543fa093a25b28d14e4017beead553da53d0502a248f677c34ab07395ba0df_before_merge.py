    def __init__(self,
                 optimizer: Union[None, Optimizer, ConfiguredOptimizer] = None,
                 space: Optional[Parameter] = None,
                 metric: Optional[str] = None,
                 mode: Optional[str] = None,
                 max_concurrent: Optional[int] = None,
                 **kwargs):
        assert ng is not None, "Nevergrad must be installed!"
        if mode:
            assert mode in ["min", "max"], "`mode` must be 'min' or 'max'."

        super(NevergradSearch, self).__init__(
            metric=metric, mode=mode, max_concurrent=max_concurrent, **kwargs)

        self._space = None
        self._opt_factory = None
        self._nevergrad_opt = None

        if isinstance(optimizer, Optimizer):
            if space is not None or isinstance(space, list):
                raise ValueError(
                    "If you pass a configured optimizer to Nevergrad, either "
                    "pass a list of parameter names or None as the `space` "
                    "parameter.")
            self._parameters = space
            self._nevergrad_opt = optimizer
        elif isinstance(optimizer, ConfiguredOptimizer):
            self._opt_factory = optimizer
            self._parameters = None
            self._space = space
        else:
            raise ValueError(
                "The `optimizer` argument passed to NevergradSearch must be "
                "either an `Optimizer` or a `ConfiguredOptimizer`.")

        self._live_trial_mapping = {}
        self.max_concurrent = max_concurrent

        if self._nevergrad_opt or self._space:
            self.setup_nevergrad()