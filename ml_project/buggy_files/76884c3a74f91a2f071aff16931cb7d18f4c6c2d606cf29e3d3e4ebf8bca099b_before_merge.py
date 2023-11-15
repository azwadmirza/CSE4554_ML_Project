    def covar_trace(self):
        variational_covar = self.variational_distribution.variational_distribution.covariance_matrix
        prior_covar = self.prior_distribution.covariance_matrix
        batch_shape = prior_covar.shape[:-2]
        return (variational_covar * prior_covar).view(*batch_shape, -1).sum(-1)