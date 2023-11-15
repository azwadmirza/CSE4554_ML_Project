    def __init__(
        self,
        num_mixtures=None,
        ard_num_dims=1,
        batch_size=1,
        active_dims=None,
        eps=1e-6,
        log_mixture_scales_prior=None,
        log_mixture_means_prior=None,
        log_mixture_weights_prior=None,
        n_mixtures=None,
        n_dims=None,
    ):
        if n_mixtures is not None:
            warnings.warn("n_mixtures is deprecated. Use num_mixtures instead.", DeprecationWarning)
            num_mixtures = n_mixtures
        if num_mixtures is None:
            raise RuntimeError("num_mixtures is a required argument")
        if n_dims is not None:
            warnings.warn("n_dims is deprecated. Use ard_num_dims instead.", DeprecationWarning)
            ard_num_dims = n_dims
        if (
            log_mixture_means_prior is not None
            or log_mixture_scales_prior is not None
            or log_mixture_weights_prior is not None
        ):
            logger.warning("Priors not implemented for SpectralMixtureKernel")

        # This kernel does not use the default lengthscale
        super(SpectralMixtureKernel, self).__init__(active_dims=active_dims)
        self.num_mixtures = num_mixtures
        self.batch_size = batch_size
        self.ard_num_dims = ard_num_dims
        self.eps = eps

        self.register_parameter(
            name="log_mixture_weights", parameter=torch.nn.Parameter(torch.zeros(self.batch_size, self.num_mixtures))
        )
        self.register_parameter(
            name="log_mixture_means",
            parameter=torch.nn.Parameter(torch.zeros(self.batch_size, self.num_mixtures, 1, self.ard_num_dims)),
        )
        self.register_parameter(
            name="log_mixture_scales",
            parameter=torch.nn.Parameter(torch.zeros(self.batch_size, self.num_mixtures, 1, self.ard_num_dims)),
        )