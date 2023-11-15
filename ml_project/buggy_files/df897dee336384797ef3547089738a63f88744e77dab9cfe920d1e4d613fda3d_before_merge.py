    def __repr__(self) -> str:
        # inspired by xarray
        parts = [f"<stan.{type(self).__name__}>"]

        def summarize_param(param_name, dims):
            return f"    {param_name}: {tuple(dims)}"

        if self.param_names:
            parts.append("Parameters:")
        for param_name, dims in zip(self.param_names, self.dims):
            parts.append(summarize_param(param_name, dims))
        if self._finished:
            # total draws is num_draws (per-chain) times num_chains
            parts.append(f"Draws: {self._draws.shape[-2] * self._draws.shape[-1]}")
        return "\n".join(parts)