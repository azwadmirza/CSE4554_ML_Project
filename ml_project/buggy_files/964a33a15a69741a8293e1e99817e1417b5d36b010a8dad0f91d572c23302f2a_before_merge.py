    def expected_log_prob(self, observations, function_dist, *params, **kwargs):
        """
        Computes the expected log likelihood (used for variational inference):

        .. math::
            \mathbb{E}_{f(x)} \left[ \log p \left( y \mid f(x) \right) \right]

        Args:
            :attr:`function_dist` (:class:`gpytorch.distributions.MultivariateNormal`)
                Distribution for :math:`f(x)`.
            :attr:`observations` (:class:`torch.Tensor`)
                Values of :math:`y`.
            :attr:`kwargs`

        Returns
            `torch.Tensor` (log probability)
        """
        log_prob_lambda = lambda function_samples: self.forward(function_samples).log_prob(observations)
        log_prob = self.quadrature(log_prob_lambda, function_dist)
        return log_prob.sum(tuple(range(-1, -len(function_dist.event_shape) - 1, -1)))