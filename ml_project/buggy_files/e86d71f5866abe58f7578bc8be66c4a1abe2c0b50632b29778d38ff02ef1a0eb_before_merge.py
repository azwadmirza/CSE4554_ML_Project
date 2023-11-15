    def distribution(self, distr_args, loc=None, scale=None) -> Distribution:
        assert loc is None and scale is None
        distr = Dirichlet(distr_args)
        return distr