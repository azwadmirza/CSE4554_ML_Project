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

        self.data = data_input_to_tensor(data)
        X_data, Y_data = self.data
        self.num_data = X_data.shape[0]
        self.q_alpha = Parameter(np.zeros((self.num_data, self.num_latent_gps)))
        self.q_lambda = Parameter(
            np.ones((self.num_data, self.num_latent_gps)), transform=gpflow.utilities.positive()
        )