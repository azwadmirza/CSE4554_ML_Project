    def _cov_alpha(self):
        """
        Estimated covariance matrix of model coefficients w/o exog
        """
        # drop exog
        return self._cov_params()[self.k_exog*self.neqs:, self.k_exog*self.neqs:]