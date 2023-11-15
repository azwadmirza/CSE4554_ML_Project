    def __init__(
        self,
        active_dims=None,
        batch_size=1,
        lengthscale_prior=None,
        period_length_prior=None,
        param_transform=softplus,
        inv_param_transform=None,
        eps=1e-6,
        **kwargs
    ):
        lengthscale_prior = _deprecate_kwarg(kwargs, "log_lengthscale_prior", "lengthscale_prior", lengthscale_prior)
        period_length_prior = _deprecate_kwarg(
            kwargs, "log_period_length_prior", "period_length_prior", period_length_prior
        )
        super(PeriodicKernel, self).__init__(
            has_lengthscale=True,
            active_dims=active_dims,
            batch_size=batch_size,
            lengthscale_prior=lengthscale_prior,
            param_transform=param_transform,
            inv_param_transform=inv_param_transform,
            eps=eps,
        )
        self.register_parameter(name="raw_period_length", parameter=torch.nn.Parameter(torch.zeros(batch_size, 1, 1)))
        if period_length_prior is not None:
            self.register_prior(
                "period_length_prior",
                period_length_prior,
                lambda: self.period_length,
                lambda v: self._set_period_length(v),
            )