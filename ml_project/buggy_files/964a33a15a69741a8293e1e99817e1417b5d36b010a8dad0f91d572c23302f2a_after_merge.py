    def expected_log_prob(self, observations, function_dist, *args, **kwargs):
        likelihood_samples = self._draw_likelihood_samples(function_dist, *args, **kwargs)
        res = likelihood_samples.log_prob(observations).mean(dim=0)
        return res