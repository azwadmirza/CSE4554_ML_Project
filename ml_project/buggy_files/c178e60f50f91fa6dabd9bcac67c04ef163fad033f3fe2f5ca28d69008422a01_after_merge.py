    def get_posterior(self, *args, **kwargs):
        """
        Returns a Delta posterior distribution for MAP inference.
        """
        loc = pyro.param("{}_loc".format(self.prefix), self._init_loc)
        return dist.Delta(loc).to_event(1)