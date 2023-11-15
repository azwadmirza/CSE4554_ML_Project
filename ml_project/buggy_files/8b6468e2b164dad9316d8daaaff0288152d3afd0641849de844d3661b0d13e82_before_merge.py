    def marginal(self, function_dist, *params, **kwargs):
        """
        Computes a predictive distribution :math:`p(y*|x*)` given either a posterior
        distribution :math:`p(f|D,x)` or a prior distribution :math:`p(f|x)` as input.

        With both exact inference and variational inference, the form of
        :math:`p(f|D,x)` or :math:`p(f|x)` should usually be Gaussian. As a result, input
        should usually be a MultivariateNormal specified by the mean and
        (co)variance of :math:`p(f|...)`.

        Args:
            :attr:`function_dist` (:class:`gpytorch.distributions.MultivariateNormal`)
                Distribution for :math:`f(x)`.
            :attr:`kwargs`

        Returns
            Distribution object (the marginal distribution, or samples from it)
        """
        sample_shape = torch.Size([settings.num_likelihood_samples.value()])
        function_samples = function_dist.rsample(sample_shape)
        return self.forward(function_samples)