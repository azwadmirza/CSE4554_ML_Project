    def __init__(
        self,
        num_dimensions,
        variance_prior=None,
        offset_prior=None,
        active_dims=None,
        variance_bounds=None,
        offset_bounds=None,
    ):
        """
        Args:
            num_dimensions (int): Number of data dimensions to expect. This is necessary to create the offset parameter.
            variance_prior (:obj:`gpytorch.priors.Prior`): Prior over the variance parameter (default `None`).
            offset_prior (:obj:`gpytorch.priors.Prior`): Prior over the offset parameter (default `None`).
            active_dims (list): List of data dimensions to operate on. `len(active_dims)` should equal `num_dimensions`.
            variance_bounds (tuple, deprecated): Min and max value for the variance parameter. Deprecated, and now
                                                 creates a :obj:`gpytorch.priors.SmoothedBoxPrior`.
            offset_bounds (tuple, deprecated): Min and max value for the offset parameter. Deprecated, and now creates a
                                                :obj:'gpytorch.priors.SmoothedBoxPrior'.
        """
        super(LinearKernel, self).__init__(active_dims=active_dims)
        variance_prior = _bounds_to_prior(prior=variance_prior, bounds=variance_bounds, log_transform=False)
        self.register_parameter(name="variance", parameter=torch.nn.Parameter(torch.zeros(1)), prior=variance_prior)
        offset_prior = _bounds_to_prior(prior=offset_prior, bounds=offset_bounds, log_transform=False)
        self.register_parameter(
            name="offset", parameter=torch.nn.Parameter(torch.zeros(1, 1, num_dimensions)), prior=offset_prior
        )