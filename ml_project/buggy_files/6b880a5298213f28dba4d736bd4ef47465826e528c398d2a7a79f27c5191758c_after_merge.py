    def forward(self, function_samples: Tensor, *params: Any, **kwargs: Any) -> base_distributions.Normal:
        noise = self._shaped_noise_covar(function_samples.shape, *params, **kwargs).diag()
        noise = noise.view(*noise.shape[:-1], *function_samples.shape[-2:])
        return base_distributions.Independent(base_distributions.Normal(function_samples, noise.sqrt()), 1)