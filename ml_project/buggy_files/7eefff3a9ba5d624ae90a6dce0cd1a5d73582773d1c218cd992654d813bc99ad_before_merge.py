    def __init__(
        self,
        stan_outputs: Tuple[bytes, ...],
        num_chains: int,
        param_names: Tuple[str, ...],
        constrained_param_names: Tuple[str, ...],
        dims: Tuple[Tuple[int, ...]],
        num_warmup: int,
        num_samples: int,
        num_thin: int,
        save_warmup: bool,
    ) -> None:
        self.stan_outputs = stan_outputs
        self.num_chains = num_chains
        assert self.num_chains == len(self.stan_outputs)
        self.param_names, self.dims, self.constrained_param_names = (
            param_names,
            dims,
            constrained_param_names,
        )
        self.num_warmup, self.num_samples = num_warmup, num_samples
        self.num_thin, self.save_warmup = num_thin, save_warmup

        # `self.sample_and_sampler_param_names` collects the sample and sampler param names.
        # - "sample params" include `lp__`, `accept_stat__`
        # - "sampler params" include `stepsize__`, `treedepth__`, ...
        # These names are gathered later in this function by inspecting the output from Stan.
        self.sample_and_sampler_param_names: Tuple[str, ...]

        num_flat_params = sum(np.product(dims_ or 1) for dims_ in dims)  # if dims == [] then it is a scalar
        assert num_flat_params == len(constrained_param_names)
        num_samples_saved = (self.num_samples + self.num_warmup * self.save_warmup) // self.num_thin

        # self._draws holds all the draws. We cannot allocate it before looking at the draws
        # because we do not know how many sampler-specific parameters are present. Later in this
        # function we count them and only then allocate the array for `self._draws`.
        #
        # _draws is an ndarray with shape (num_sample_and_sampler_params + num_flat_params, num_draws, num_chains)
        self._draws: np.ndarray

        parser = simdjson.Parser()
        for chain_index, stan_output in zip(range(self.num_chains), self.stan_outputs):
            draw_index = 0
            for line in stan_output.splitlines():
                try:
                    msg = parser.parse(line)
                except ValueError:
                    # Occurs when draws contain an nan or infinity. simdjson cannot parse such values.
                    msg = json.loads(line)
                if msg["topic"] == "sample":
                    # Ignore sample message which is mixed together with proper draws.
                    if not isinstance(msg["values"], (simdjson.Object, dict)):
                        continue

                    # for the first draw: collect sample and sampler parameter names.
                    if not hasattr(self, "_draws"):
                        feature_names = cast(Tuple[str, ...], tuple(msg["values"].keys()))
                        self.sample_and_sampler_param_names = tuple(
                            name for name in feature_names if name.endswith("__")
                        )
                        num_rows = len(self.sample_and_sampler_param_names) + num_flat_params
                        # column-major order ("F") aligns with how the draws are stored (in cols).
                        self._draws = np.empty((num_rows, num_samples_saved, num_chains), order="F")
                        # rudimentary check of parameter order (sample & sampler params must be first)
                        if num_flat_params and feature_names[-1].endswith("__"):
                            raise RuntimeError(
                                f"Expected last parameter name to be one declared in program code, found `{feature_names[-1]}`"
                            )

                    draw_row = tuple(msg["values"].values())  # a "row" of values from a single draw from Stan C++
                    self._draws[:, draw_index, chain_index] = draw_row
                    draw_index += 1
            assert draw_index == num_samples_saved
        # set draws array to read-only, also indicates we are finished
        assert self.sample_and_sampler_param_names and self._draws.size
        self._draws.flags["WRITEABLE"] = False