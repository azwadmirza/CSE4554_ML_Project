    def __init__(
        self,
        data: RegressionData,
        kernel: Kernel,
        likelihood: Likelihood,
        mean_function: Optional[MeanFunction] = None,
        num_latent_gps: Optional[int] = None,
    ):
        """
        data = (X, Y) contains the input points [N, D] and the observations [N, P]
        kernel, likelihood, mean_function are appropriate GPflow objects
        """
        if num_latent_gps is None:
            num_latent_gps = self.calc_num_latent_gps_from_data(data, kernel, likelihood)
        super().__init__(kernel, likelihood, mean_function, num_latent_gps)

        X_data, Y_data = data
        num_data = X_data.shape[0]
        self.num_data = num_data
        self.data = data

        self.q_mu = Parameter(np.zeros((num_data, self.num_latent_gps)))
        q_sqrt = np.array([np.eye(num_data) for _ in range(self.num_latent_gps)])
        self.q_sqrt = Parameter(q_sqrt, transform=triangular())