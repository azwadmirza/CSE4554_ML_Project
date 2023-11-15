    def _cov_alpha(self):
        """
        Estimated covariance matrix of model coefficients ex intercept
        """
        # drop intercept and trend
        return self.cov_params[self.k_trend*self.neqs:, self.k_trend*self.neqs:]