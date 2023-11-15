    def _parameter_indexes(self, param: str) -> Tuple[int, ...]:
        """Obtain indexes for values associated with `param`.

        A draw from the sampler is a flat vector of values. A multi-dimensional
        variable will be stored in this vector in column-major order. This function
        identifies the indices which allow us to extract values associated with a
        parameter.

        Parameters
        ----------
        param : Parameter of interest.

        Returns
        -------
        Indexes associated with parameter.

        Note
        ----

        This function assumes that parameters appearing in the program code follow
        the sample and sampler parameters (e.g., ``lp__``, ``stepsize__``).
        """
        # if `param` is a scalar, it will match one of the constrained names or it will match a
        # sample param name (e.g., `lp__`) or a sampler param name (e.g., `stepsize__`)
        if param in self.sample_and_sampler_param_names:
            return (self.sample_and_sampler_param_names.index(param),)
        sample_and_sampler_params_offset = len(self.sample_and_sampler_param_names)
        if param in self.constrained_param_names:
            return (sample_and_sampler_params_offset + self.constrained_param_names.index(param),)

        def calculate_starts(dims: Tuple[Tuple[int, ...]]) -> Tuple[int, ...]:
            """Calculate starting indexes given dims."""
            s = [cast(int, np.prod(d)) for d in dims]
            starts = np.cumsum([0] + s)[: len(dims)]
            return tuple(int(i) for i in starts)

        starts = tuple(sample_and_sampler_params_offset + i for i in calculate_starts(self.dims))
        names_index = self.param_names.index(param)
        flat_param_count = cast(int, np.prod(self.dims[names_index]))
        return tuple(starts[names_index] + offset for offset in range(flat_param_count))