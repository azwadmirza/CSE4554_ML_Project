    def random(self, point=None, size=None):
        """
        Draw random values from Triangular distribution.

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
        c, lower, upper = draw_values([self.c, self.lower, self.upper],
                                      point=point, size=size)
        return generate_samples(self._random, c=c, lower=lower, upper=upper,
                                size=size, dist_shape=self.shape)