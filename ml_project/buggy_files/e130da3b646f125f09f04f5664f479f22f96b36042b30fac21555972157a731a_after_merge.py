    def _cov_alpha(self):
        """
        Estimated covariance matrix of model coefficients w/o exog
        """
        # drop exog
        kn = self.k_exog * self.neqs
        return self.cov_params()[kn:, kn:]