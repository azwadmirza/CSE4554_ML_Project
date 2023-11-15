    def marginal(self, function_dist, *args, **kwargs):
        res = self._draw_likelihood_samples(function_dist, *args, **kwargs)
        return res