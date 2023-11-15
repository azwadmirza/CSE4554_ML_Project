    def _restore_or_init_optimizer(
        self,
        completed_trials: "List[optuna.trial.FrozenTrial]",
        search_space: Dict[str, BaseDistribution],
        ordered_keys: List[str],
    ) -> CMA:

        # Restore a previous CMA object.
        for trial in reversed(completed_trials):
            serialized_optimizer = trial.system_attrs.get(
                "cma:optimizer", None
            )  # type: Optional[str]
            if serialized_optimizer is None:
                continue
            return pickle.loads(bytes.fromhex(serialized_optimizer))

        # Init a CMA object.
        if self._x0 is None:
            self._x0 = _initialize_x0(search_space)

        if self._sigma0 is None:
            sigma0 = _initialize_sigma0(search_space)
        else:
            sigma0 = self._sigma0
        sigma0 = max(sigma0, _MIN_SIGMA0)
        mean = np.array([self._x0[k] for k in ordered_keys])
        bounds = _get_search_space_bound(ordered_keys, search_space)
        n_dimension = len(ordered_keys)
        return CMA(
            mean=mean,
            sigma=sigma0,
            bounds=bounds,
            seed=self._cma_rng.randint(1, 2 ** 32),
            n_max_resampling=10 * n_dimension,
        )