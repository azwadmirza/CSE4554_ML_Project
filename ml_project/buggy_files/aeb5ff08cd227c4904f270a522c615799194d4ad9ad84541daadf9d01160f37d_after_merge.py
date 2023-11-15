    def random(self, point=None, size=None):
        """
        Draw random values from TruncatedNormal distribution.

        Parameters
        ----------
        point : dict, optional
            Dict of variable values on which random values are to be
            conditioned (uses default point if not specified).
        size : int, optional
            Desired size of random sample (returns one sample if not
            specified).

        Returns
        -------
        array
        """
        mu, sigma, lower, upper = draw_values(
            [self.mu, self.sigma, self.lower, self.upper],
            point=point,
            size=size
        )
        return generate_samples(
            self._random,
            mu=mu,
            sigma=sigma,
            lower=lower,
            upper=upper,
            dist_shape=self.shape,
            size=size,
        )