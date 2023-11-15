    def __init__(
        self,
        active_dims=None,
        batch_size=1,
        period_length_prior=None,
        eps=1e-6,
        param_transform=softplus,
        inv_param_transform=None,
        **kwargs
    ):
        super(CosineKernel, self).__init__(
            active_dims=active_dims, param_transform=param_transform, inv_param_transform=inv_param_transform
        )
        self.eps = eps
        self.register_parameter(name="raw_period_length", parameter=torch.nn.Parameter(torch.zeros(batch_size, 1, 1)))
        if period_length_prior is not None:
            self.register_prior(
                "period_length_prior",
                period_length_prior,
                lambda: self.period_length,
                lambda v: self._set_period_length(v),
            )