    def distribution(self, distr_args, loc=None, scale=None) -> Distribution:
        distr = DirichletMultinomial(self.dim, self.n_trials, distr_args)
        return distr