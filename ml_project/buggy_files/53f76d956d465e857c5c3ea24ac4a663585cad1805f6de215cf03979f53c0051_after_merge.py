    def __getitem__(self, param):
        """Returns array with shape (stan_dimensions, num_chains * num_samples)"""
        assert param.endswith("__") or param in self.param_names, param
        param_indexes = self._parameter_indexes(param)
        param_dim = [] if param in self.sample_and_sampler_param_names else self.dims[self.param_names.index(param)]
        # fmt: off
        num_samples_saved = (self.num_samples + self.num_warmup * self.save_warmup) // self.num_thin
        assert self._draws.shape == (len(self.sample_and_sampler_param_names) + len(self.constrained_param_names), num_samples_saved, self.num_chains)
        # fmt: on
        # Stack chains together. Parameter is still stored flat.
        view = self._draws[param_indexes, :, :].reshape(len(param_indexes), -1).view()
        assert view.shape == (len(param_indexes), num_samples_saved * self.num_chains)
        # reshape must yield something with least two dimensions
        reshape_args = param_dim + [-1] if param_dim else (1, -1)
        # reshape, recover the shape of the stan parameter
        return view.reshape(*reshape_args, order="F")