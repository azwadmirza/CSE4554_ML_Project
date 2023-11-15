    def forward(self, output, target, **kwargs):
        """
        Computes the MLL given :math:`p(\mathbf f)` and `\mathbf y`

        Args:
            :attr:`output` (:obj:`gpytorch.distributions.MultivariateNormal`):
                :math:`p(\mathbf f)` (or approximation)
                the outputs of the latent function (the :obj:`gpytorch.models.GP`)
            :attr:`target` (`torch.Tensor`):
                :math:`\mathbf y` The target values
            :attr:`**kwargs`:
                Additional arguments to pass to the likelihood's :attr:`forward` function.
        """
        raise NotImplementedError