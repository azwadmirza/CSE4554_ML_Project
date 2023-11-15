    def __init__(
        self,
        num_dimensions,
        variance_prior=None,
        offset_prior=None,
        active_dims=None,
        variance_bounds=None,
        offset_bounds=None,
    ):
        super(LinearKernel, self).__init__(active_dims=active_dims)
        variance_prior = _bounds_to_prior(prior=variance_prior, bounds=variance_bounds, log_transform=False)
        self.register_parameter(name="variance", parameter=torch.nn.Parameter(torch.zeros(1)), prior=variance_prior)
        offset_prior = _bounds_to_prior(prior=offset_prior, bounds=offset_bounds, log_transform=False)
        self.register_parameter(
            name="offset", parameter=torch.nn.Parameter(torch.zeros(1, 1, num_dimensions)), prior=offset_prior
        )