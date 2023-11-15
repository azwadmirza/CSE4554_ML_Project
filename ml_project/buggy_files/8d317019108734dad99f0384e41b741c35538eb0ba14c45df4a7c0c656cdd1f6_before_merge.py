    def _cov_alpha(self):
        """
        Estimated covariance matrix of model coefficients ex intercept
        """
        # drop intercept
        return self.cov_params[self.neqs:, self.neqs:]