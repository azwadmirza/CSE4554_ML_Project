    def cov_params(self):
        """Estimated variance-covariance of model coefficients

        Notes
        -----
        Covariance of vec(B), where B is the matrix
        [params_for_deterministic_terms, A_1, ..., A_p] with the shape
        (K x (Kp + number_of_deterministic_terms))
        Adjusted to be an unbiased estimator
        Ref: Lütkepohl p.74-75
        """
        import warnings
        warnings.warn("For consistency with other statmsodels models, "
                      "starting in version 0.11.0 `VARResults.cov_params` "
                      "will be a method instead of a property.",
                      category=FutureWarning)
        z = self.endog_lagged
        return np.kron(scipy.linalg.inv(np.dot(z.T, z)), self.sigma_u)