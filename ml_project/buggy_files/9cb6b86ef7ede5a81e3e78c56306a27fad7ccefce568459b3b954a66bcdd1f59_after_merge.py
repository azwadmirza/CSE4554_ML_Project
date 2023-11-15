    def __call__(self, inputs, are_samples=False, **kwargs):
        """
        Forward data through this hidden GP layer. The output is a MultitaskMultivariateNormal distribution
        (or MultivariateNormal distribution is output_dims=None).

        If the input is >=2 dimensional Tensor (e.g. `n x d`), we pass the input through each hidden GP,
        resulting in a `n x h` multitask Gaussian distribution (where all of the `h` tasks represent an
        output dimension and are independent from one another).  We then draw `s` samples from these Gaussians,
        resulting in a `s x n x h` MultitaskMultivariateNormal distribution.

        If the input is a >=3 dimensional Tensor, and the `are_samples=True` kwarg is set, then we assume that
        the outermost batch dimension is a samples dimension. The output will have the same number of samples.
        For example, a `s x b x n x d` input will result in a `s x b x n x h` MultitaskMultivariateNormal distribution.

        The goal of these last two points is that if you have a tensor `x` that is `n x d`, then:
            >>> hidden_gp2(hidden_gp(x))

        will just work, and return a tensor of size `s x n x h2`, where `h2` is the output dimensionality of
        hidden_gp2. In this way, hidden GP layers are easily composable.
        """
        deterministic_inputs = not are_samples
        if isinstance(inputs, MultitaskMultivariateNormal):
            inputs = torch.distributions.Normal(loc=inputs.mean, scale=inputs.variance.sqrt()).rsample()
            deterministic_inputs = False

        if settings.debug.on():
            if not torch.is_tensor(inputs):
                raise ValueError(
                    "`inputs` should either be a MultitaskMultivariateNormal or a Tensor, got "
                    f"{inputs.__class__.__Name__}"
                )

            if inputs.size(-1) != self.input_dims:
                raise RuntimeError(
                    f"Input shape did not match self.input_dims. Got total feature dims [{inputs.size(-1)}],"
                    f" expected [{self.input_dims}]"
                )

        # Repeat the input for all possible outputs
        if self.output_dims is not None:
            inputs = inputs.unsqueeze(-3)
            inputs = inputs.expand(*inputs.shape[:-3], self.output_dims, *inputs.shape[-2:])

        # Now run samples through the GP
        output = ApproximateGP.__call__(self, inputs)
        if self.output_dims is not None:
            mean = output.loc.transpose(-1, -2)
            covar = BlockDiagLazyTensor(output.lazy_covariance_matrix, block_dim=-3)
            output = MultitaskMultivariateNormal(mean, covar, interleaved=False)

        # Maybe expand inputs?
        if deterministic_inputs:
            output = output.expand(torch.Size([settings.num_likelihood_samples.value()]) + output.batch_shape)

        return output