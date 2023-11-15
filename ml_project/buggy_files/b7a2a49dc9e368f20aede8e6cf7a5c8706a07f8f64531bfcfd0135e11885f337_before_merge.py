    def get_posterior(self, *args, **kwargs):
        """
        Returns a diagonal Normal posterior distribution.
        """
        loc = pyro.param("{}_loc".format(self.prefix),
                         lambda: torch.zeros(self.latent_dim))
        scale = pyro.param("{}_scale".format(self.prefix),
                           lambda: torch.ones(self.latent_dim),
                           constraint=constraints.positive)
        return dist.Normal(loc, scale).to_event(1)