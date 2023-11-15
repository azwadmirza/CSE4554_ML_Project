    def get_posterior(self, *args, **kwargs):
        """
        Returns a MultivariateNormal posterior distribution.
        """
        loc = pyro.param("{}_loc".format(self.prefix),
                         lambda: torch.zeros(self.latent_dim))
        scale_tril = pyro.param("{}_scale_tril".format(self.prefix),
                                lambda: torch.eye(self.latent_dim),
                                constraint=constraints.lower_cholesky)
        return dist.MultivariateNormal(loc, scale_tril=scale_tril)