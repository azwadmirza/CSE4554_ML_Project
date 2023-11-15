    def initialize_variational_distribution(self, prior_dist):
        self.variational_mean.data.copy_(prior_dist.mean)
        self.variational_mean.data.add_(self.mean_init_std, torch.randn_like(prior_dist.mean))
        self.chol_variational_covar.data.copy_(prior_dist.lazy_covariance_matrix.cholesky().evaluate())