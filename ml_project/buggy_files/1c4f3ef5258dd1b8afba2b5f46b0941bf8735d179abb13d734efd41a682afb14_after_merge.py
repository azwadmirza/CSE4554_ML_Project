    def _shaped_noise_covar(self, base_shape: torch.Size, *params: Any, **kwargs: Any):
        return self.noise_covar(*params, shape=base_shape, **kwargs)