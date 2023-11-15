    def __init__(self, noise_prior=None, batch_size=1, param_transform=softplus, inv_param_transform=None, **kwargs):
        noise_covar = HomoskedasticNoise(
            noise_prior=noise_prior,
            batch_size=batch_size,
            param_transform=param_transform,
            inv_param_transform=inv_param_transform,
        )
        super().__init__(noise_covar=noise_covar)