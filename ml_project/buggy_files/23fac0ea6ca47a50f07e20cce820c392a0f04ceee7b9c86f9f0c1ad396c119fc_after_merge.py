    def __init__(
        self,
        has_lengthscale=False,
        ard_num_dims=None,
        batch_size=1,
        active_dims=None,
        log_lengthscale_bounds=None,
        log_lengthscale_prior=None,
        eps=1e-6,
    ):
        super(Kernel, self).__init__()
        if active_dims is not None and not torch.is_tensor(active_dims):
            active_dims = torch.tensor(active_dims, dtype=torch.long)
        self.active_dims = active_dims
        self.ard_num_dims = ard_num_dims
        self.batch_size = batch_size
        self.__has_lengthscale = has_lengthscale
        if has_lengthscale:
            lengthscale_num_dims = 1 if ard_num_dims is None else ard_num_dims
            log_lengthscale_prior = _bounds_to_prior(prior=log_lengthscale_prior, bounds=log_lengthscale_bounds)
            self.register_parameter(
                name="log_lengthscale",
                parameter=torch.nn.Parameter(torch.zeros(batch_size, 1, lengthscale_num_dims)),
                prior=log_lengthscale_prior,
            )