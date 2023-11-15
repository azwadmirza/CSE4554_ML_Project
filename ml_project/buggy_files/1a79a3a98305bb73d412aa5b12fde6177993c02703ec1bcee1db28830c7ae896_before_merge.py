    def forward(self, output, target):
        """
        Args:
        - output: (MultivariateNormal) - the outputs of the latent function
        - target: (Variable) - the target values
        """
        raise NotImplementedError