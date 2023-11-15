    def expected_log_prob(self, target: Tensor, input: MultivariateNormal, *params: Any, **kwargs: Any) -> Tensor:
        mean, variance = input.mean, input.variance
        num_event_dim = len(input.event_shape)

        noise = self._shaped_noise_covar(mean.shape, *params, **kwargs).diag()
        # Potentially reshape the noise to deal with the multitask case
        noise = noise.view(*noise.shape[:-1], *input.event_shape)

        res = (((target - mean) ** 2 + variance) / noise + noise.log() + math.log(2 * math.pi))
        res = res.mul(-0.5)
        if num_event_dim > 1:  # Do appropriate summation for multitask Gaussian likelihoods
            res = res.sum(list(range(-1, -num_event_dim, -1)))
        return res