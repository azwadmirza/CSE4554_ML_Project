        def marginal(self, function_dist, *args, **kwargs):
            r"""
            Computes a predictive distribution :math:`p(y^* | \mathbf x^*)` given either a posterior
            distribution :math:`p(\mathbf f | \mathcal D, \mathbf x)` or a
            prior distribution :math:`p(\mathbf f|\mathbf x)` as input.

            With both exact inference and variational inference, the form of
            :math:`p(\mathbf f|\mathcal D, \mathbf x)` or :math:`p(\mathbf f|
            \mathbf x)` should usually be Gaussian. As a result, :attr:`function_dist`
            should usually be a :obj:`~gpytorch.distributions.MultivariateNormal` specified by the mean and
            (co)variance of :math:`p(\mathbf f|...)`.

            Args:
                :attr:`function_dist` (:class:`~gpytorch.distributions.MultivariateNormal`)
                    Distribution for :math:`f(x)`.
                :attr:`args`, :attr:`kwargs`
                    Passed to the `forward` function

            Returns:
                Distribution object (the marginal distribution, or samples from it)
            """
            return super().marginal(function_dist, *args, **kwargs)