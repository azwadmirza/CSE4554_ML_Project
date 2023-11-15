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
        mu_v, std_v, a_v, b_v = draw_values(
            [self.mu, self.sigma, self.lower, self.upper], point=point, size=size)
        return generate_samples(stats.truncnorm.rvs,
                                a=(a_v - mu_v)/std_v,
                                b=(b_v - mu_v) / std_v,
                                loc=mu_v,
                                scale=std_v,
                                dist_shape=self.shape,
                                size=size,
                                )