    def __call__(self, input, *params, **kwargs):
        # Conditional
        if torch.is_tensor(input):
            return super().__call__(input, *params, **kwargs)
        # Marginal
        elif isinstance(input, MultivariateNormal):
            return self.marginal(input, *params, **kwargs)
        # Error
        else:
            raise RuntimeError(
                "Likelihoods expects a MultivariateNormal input to make marginal predictions, or a "
                "torch.Tensor for conditional predictions. Got a {}".format(input.__class__.__name__)
            )