    def random(self, point=None, size=None):
        """
        Draw random values from Rice distribution.

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
        nu, sigma = draw_values([self.nu, self.sigma],
                             point=point, size=size)
        return generate_samples(self._random, nu=nu, sigma=sigma,
                                dist_shape=self.shape, size=size)