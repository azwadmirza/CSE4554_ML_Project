    def distribution(self, distr_args, loc=None, scale=None) -> Distribution:
        distr = Dirichlet(distr_args)
        return distr