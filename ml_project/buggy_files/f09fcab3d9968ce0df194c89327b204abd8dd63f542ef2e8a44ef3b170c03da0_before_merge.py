    def kl_divergence(self):
        variational_dist_u = self.variational_distribution.variational_distribution
        prior_dist = self.prior_distribution
        kl_divergence = 0.5 * sum(
            [
                # log|k| - log|S|
                # = log|K| - log|K var_dist_covar K|
                # = -log|K| - log|var_dist_covar|
                self.prior_covar_logdet(),
                -variational_dist_u.lazy_covariance_matrix.logdet(),
                # tr(K^-1 S) = tr(K^1 K var_dist_covar K) = tr(K var_dist_covar)
                self.covar_trace(),
                # (m - \mu u)^T K^-1 (m - \mu u)
                # = (K^-1 (m - \mu u)) K (K^1 (m - \mu u))
                # = (var_dist_mean)^T K (var_dist_mean)
                self.mean_diff_inv_quad(),
                # d
                -prior_dist.event_shape.numel(),
            ]
        )

        return kl_divergence