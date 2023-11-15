    def __init__(
        self,
        has_lengthscale=False,
        ard_num_dims=None,
        batch_size=1,
        active_dims=None,
        lengthscale_prior=None,
        param_transform=softplus,
        inv_param_transform=None,
        eps=1e-6,
        **kwargs
    ):
        super(Kernel, self).__init__()
        if active_dims is not None and not torch.is_tensor(active_dims):
            active_dims = torch.tensor(active_dims, dtype=torch.long)
        self.register_buffer("active_dims", active_dims)
        self.ard_num_dims = ard_num_dims
        self.batch_size = batch_size
        self.__has_lengthscale = has_lengthscale
        self._param_transform = param_transform
        self._inv_param_transform = _get_inv_param_transform(param_transform, inv_param_transform)
        if has_lengthscale:
            self.eps = eps
            lengthscale_num_dims = 1 if ard_num_dims is None else ard_num_dims
            self.register_parameter(
                name="raw_lengthscale", parameter=torch.nn.Parameter(torch.zeros(batch_size, 1, lengthscale_num_dims))
            )
            if lengthscale_prior is not None:
                self.register_prior(
                    "lengthscale_prior", lengthscale_prior, lambda: self.lengthscale, lambda v: self._set_lengthscale(v)
                )

        # TODO: Remove this on next official PyTorch release.
        self.__pdist_supports_batch = True