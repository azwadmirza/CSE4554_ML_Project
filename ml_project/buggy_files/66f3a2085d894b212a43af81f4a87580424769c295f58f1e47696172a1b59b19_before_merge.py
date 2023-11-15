    def forward(self, function_samples, *params, **kwargs):
        """
        Computes the conditional distribution p(y|f) that defines the likelihood.

        Args:
            :attr:`function_samples`
                Samples from the function `f`
            :attr:`kwargs`

        Returns:
            Distribution object (with same shape as :attr:`function_samples`)
        """
        raise NotImplementedError