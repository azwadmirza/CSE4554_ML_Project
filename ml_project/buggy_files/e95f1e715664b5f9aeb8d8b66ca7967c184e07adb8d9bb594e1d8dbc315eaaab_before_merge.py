    def __init__(
        self,
        log_lengthscale_prior=None,
        log_period_length_prior=None,
        eps=1e-5,
        active_dims=None,
        log_lengthscale_bounds=None,
        log_period_length_bounds=None,
    ):
        log_period_length_prior = _bounds_to_prior(prior=log_period_length_prior, bounds=log_period_length_bounds)
        super(PeriodicKernel, self).__init__(
            has_lengthscale=True,
            active_dims=active_dims,
            log_lengthscale_prior=log_lengthscale_prior,
            log_lengthscale_bounds=log_lengthscale_bounds,
        )
        self.eps = eps
        self.register_parameter(
            name="log_period_length", parameter=torch.nn.Parameter(torch.zeros(1, 1, 1)), prior=log_period_length_prior
        )