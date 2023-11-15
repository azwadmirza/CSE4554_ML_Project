    def get_posterior(self, *args, **kwargs):
        """
        Returns a diagonal Normal posterior distribution.
        """
        loc = pyro.param("{}_loc".format(self.prefix), self._init_loc)
        scale = pyro.param("{}_scale".format(self.prefix),
                           lambda: loc.new_ones(self.latent_dim),
                           constraint=constraints.positive)
        return dist.Normal(loc, scale).to_event(1)