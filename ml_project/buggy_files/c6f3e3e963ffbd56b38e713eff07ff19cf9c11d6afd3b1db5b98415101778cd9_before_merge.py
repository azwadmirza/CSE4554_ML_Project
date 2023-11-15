    def _normalization(self):
        mu, sigma = self.mu, self.sigma

        if self.lower is None and self.upper is None:
            return 0.

        if self.lower is not None and self.upper is not None:
            lcdf_a = normal_lcdf(mu, sigma, self.lower)
            lcdf_b = normal_lcdf(mu, sigma, self.upper)
            lsf_a = normal_lccdf(mu, sigma, self.lower)
            lsf_b = normal_lccdf(mu, sigma, self.upper)

            return tt.switch(
                self.lower > 0,
                logdiffexp(lsf_a, lsf_b),
                logdiffexp(lcdf_b, lcdf_a),
            )

        if self.lower is not None:
            return normal_lccdf(mu, sigma, self.lower)
        else:
            return normal_lcdf(mu, sigma, self.upper)