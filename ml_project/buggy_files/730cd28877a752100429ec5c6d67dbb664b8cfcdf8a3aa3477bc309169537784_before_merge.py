    def expected_log_prob(self, target: Tensor, input: MultivariateNormal, *params: Any, **kwargs: Any) -> Tensor:
        mean, variance = input.mean, input.variance
        noise = self.noise_covar.noise

        res = ((target - mean) ** 2 + variance) / noise + noise.log() + math.log(2 * math.pi)
        return res.mul(-0.5).sum(-1)