    def distribution(self, distr_args, loc=None, scale=None) -> Distribution:
        assert loc is None and scale is None
        distr = DirichletMultinomial(self.dim, self.n_trials, distr_args)
        return distr