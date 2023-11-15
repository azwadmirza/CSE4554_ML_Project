    def random(self, point=None, size=None):
        """
        Draw random values from ZeroInflatedNegativeBinomial distribution.

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
        mu, alpha, psi = draw_values(
            [self.mu, self.alpha, self.psi], point=point, size=size)
        g = generate_samples(stats.gamma.rvs, alpha, scale=mu / alpha,
                             dist_shape=self.shape,
                             size=size)
        g[g == 0] = np.finfo(float).eps  # Just in case
        g, psi = broadcast_distribution_samples([g, psi], size=size)
        return stats.poisson.rvs(g) * (np.random.random(g.shape) < psi)