    def __init__(
        self,
        num_mixtures=None,
        ard_num_dims=1,
        batch_size=1,
        active_dims=None,
        eps=1e-6,
        mixture_scales_prior=None,
        mixture_means_prior=None,
        mixture_weights_prior=None,
        param_transform=softplus,
        inv_param_transform=None,
        **kwargs
    ):
        if num_mixtures is None:
            raise RuntimeError("num_mixtures is a required argument")
        if mixture_means_prior is not None or mixture_scales_prior is not None or mixture_weights_prior is not None:
            logger.warning("Priors not implemented for SpectralMixtureKernel")

        # This kernel does not use the default lengthscale
        super(SpectralMixtureKernel, self).__init__(
            active_dims=active_dims, param_transform=param_transform, inv_param_transform=inv_param_transform
        )
        self.num_mixtures = num_mixtures
        self.batch_size = batch_size
        self.ard_num_dims = ard_num_dims
        self.eps = eps

        self.register_parameter(
            name="raw_mixture_weights", parameter=torch.nn.Parameter(torch.zeros(self.batch_size, self.num_mixtures))
        )
        ms_shape = torch.Size([self.batch_size, self.num_mixtures, 1, self.ard_num_dims])
        self.register_parameter(name="raw_mixture_means", parameter=torch.nn.Parameter(torch.zeros(ms_shape)))
        self.register_parameter(name="raw_mixture_scales", parameter=torch.nn.Parameter(torch.zeros(ms_shape)))