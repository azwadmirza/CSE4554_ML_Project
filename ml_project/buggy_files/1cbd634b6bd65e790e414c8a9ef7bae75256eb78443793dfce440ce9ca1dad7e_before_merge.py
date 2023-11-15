        def __call__(self, input, *params, **kwargs):
            # Conditional
            if torch.is_tensor(input):
                return super().__call__(input, *params, **kwargs)
            # Marginal
            elif any([
                isinstance(input, MultivariateNormal),
                isinstance(input, pyro.distributions.Normal),
                (
                    isinstance(input, pyro.distributions.Independent)
                    and isinstance(input.base_dist, pyro.distributions.Normal)
                ),
            ]):
                return self.marginal(input, *params, **kwargs)
            # Error
            else:
                raise RuntimeError(
                    "Likelihoods expects a MultivariateNormal or Normal input to make marginal predictions, or a "
                    "torch.Tensor for conditional predictions. Got a {}".format(input.__class__.__name__)
                )