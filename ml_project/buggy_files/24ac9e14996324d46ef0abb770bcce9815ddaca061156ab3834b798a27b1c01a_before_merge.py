    def __init__(
        self,
        n_mixtures,
        n_dims=1,
        log_mixture_weight_prior=None,
        log_mixture_mean_prior=None,
        log_mixture_scale_prior=None,
        active_dims=None,
    ):
        self.n_mixtures = n_mixtures
        self.n_dims = n_dims
        if (
            log_mixture_mean_prior is not None
            or log_mixture_scale_prior is not None
            or log_mixture_weight_prior is not None
        ):
            logger.warning("Priors not implemented for SpectralMixtureKernel")

        super(SpectralMixtureKernel, self).__init__(active_dims=active_dims)
        self.register_parameter(name="log_mixture_weights", parameter=torch.nn.Parameter(torch.zeros(self.n_mixtures)))
        self.register_parameter(
            name="log_mixture_means", parameter=torch.nn.Parameter(torch.zeros(self.n_mixtures, self.n_dims))
        )
        self.register_parameter(
            name="log_mixture_scales", parameter=torch.nn.Parameter(torch.zeros(self.n_mixtures, self.n_dims))
        )