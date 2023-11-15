    def __init__(
        self,
        has_lengthscale=False,
        ard_num_dims=None,
        log_lengthscale_prior=None,
        active_dims=None,
        batch_size=1,
        log_lengthscale_bounds=None,
    ):
        """
        The base Kernel class handles both lengthscales and ARD.

        Args:
            has_lengthscale (bool): If True, we will register a :obj:`torch.nn.Parameter` named `log_lengthscale`
            ard_num_dims (int): If not None, the `log_lengthscale` parameter will have this many entries.
            log_lengthscale_prior (:obj:`gpytorch.priors.Prior`): Prior over the log lengthscale
            active_dims (list): List of data dimensions to evaluate this Kernel on.
            batch_size (int): If training or testing multiple GPs simultaneously, this is how many lengthscales to
                              register.
            log_lengthscale_bounds (tuple): Deprecated min and max values for the lengthscales. If supplied, this
                                            now registers a :obj:`gpytorch.priors.SmoothedBoxPrior`
        """
        super(Kernel, self).__init__()
        if active_dims is not None and not torch.is_tensor(active_dims):
            active_dims = torch.tensor(active_dims, dtype=torch.long)
        self.active_dims = active_dims
        self.ard_num_dims = ard_num_dims
        self.has_lengthscale = has_lengthscale
        if has_lengthscale:
            lengthscale_num_dims = 1 if ard_num_dims is None else ard_num_dims
            log_lengthscale_prior = _bounds_to_prior(prior=log_lengthscale_prior, bounds=log_lengthscale_bounds)
            self.register_parameter(
                name="log_lengthscale",
                parameter=torch.nn.Parameter(torch.zeros(batch_size, 1, lengthscale_num_dims)),
                prior=log_lengthscale_prior,
            )