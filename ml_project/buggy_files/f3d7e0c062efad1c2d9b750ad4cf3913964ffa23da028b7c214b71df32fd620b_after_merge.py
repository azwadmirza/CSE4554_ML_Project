    def mean_diff_inv_quad(self):
        prior_mean = self.prior_distribution.mean
        prior_covar = self.prior_distribution.lazy_covariance_matrix
        variational_mean = self.variational_distribution.mean
        return prior_covar.inv_quad(variational_mean - prior_mean)