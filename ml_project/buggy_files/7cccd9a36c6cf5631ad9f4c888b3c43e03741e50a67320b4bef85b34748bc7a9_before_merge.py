    def __init__(
        self,
        base_kernel,
        batch_size=1,
        outputscale_prior=None,
        param_transform=softplus,
        inv_param_transform=None,
        **kwargs
    ):
        outputscale_prior = _deprecate_kwarg(kwargs, "log_outputscale_prior", "outputscale_prior", outputscale_prior)
        super(ScaleKernel, self).__init__(has_lengthscale=False, batch_size=batch_size)
        self.base_kernel = base_kernel
        self._param_transform = param_transform
        self._inv_param_transform = _get_inv_param_transform(param_transform, inv_param_transform)
        self.register_parameter(name="raw_outputscale", parameter=torch.nn.Parameter(torch.zeros(batch_size)))
        if outputscale_prior is not None:
            self.register_prior(
                "outputscale_prior", outputscale_prior, lambda: self.outputscale, lambda v: self._set_outputscale(v)
            )