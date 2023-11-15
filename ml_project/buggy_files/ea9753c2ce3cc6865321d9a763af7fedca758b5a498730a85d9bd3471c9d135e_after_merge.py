    def __init__(
        self,
        nu=2.5,
        ard_num_dims=None,
        batch_size=1,
        active_dims=None,
        eps=1e-6,
        log_lengthscale_prior=None,
        log_lengthscale_bounds=None,
    ):
        if nu not in {0.5, 1.5, 2.5}:
            raise RuntimeError("nu expected to be 0.5, 1.5, or 2.5")
        super(MaternKernel, self).__init__(
            has_lengthscale=True,
            ard_num_dims=ard_num_dims,
            log_lengthscale_prior=log_lengthscale_prior,
            active_dims=active_dims,
            batch_size=batch_size,
            log_lengthscale_bounds=log_lengthscale_bounds,
        )
        self.nu = nu
        self.eps = eps