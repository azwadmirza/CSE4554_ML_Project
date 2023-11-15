    def get_posterior(self, *args, **kwargs):
        """
        Returns a LowRankMultivariateNormal posterior distribution.
        """
        loc = pyro.param("{}_loc".format(self.prefix), self._init_loc)
        factor = pyro.param("{}_cov_factor".format(self.prefix),
                            lambda: loc.new_empty(self.latent_dim, self.rank).normal_(0, (0.5 / self.rank) ** 0.5))
        diagonal = pyro.param("{}_cov_diag".format(self.prefix),
                              lambda: loc.new_full((self.latent_dim,), 0.5),
                              constraint=constraints.positive)
        return dist.LowRankMultivariateNormal(loc, factor, diagonal)