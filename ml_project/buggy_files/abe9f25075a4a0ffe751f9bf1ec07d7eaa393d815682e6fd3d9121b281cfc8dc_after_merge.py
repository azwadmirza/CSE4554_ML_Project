    def __init__(
        self,
        distribution_class: Type[tfp.distributions.Distribution] = tfp.distributions.Normal,
        scale_transform: Optional[tfp.bijectors.Bijector] = None,
        **kwargs,
    ):
        """
        :param distribution_class: distribution class parameterized by `loc` and `scale`
            as first and second argument, respectively.
        :param scale_transform: callable/bijector applied to the latent
            function modelling the scale to ensure its positivity.
            Typically, `tf.exp` or `tf.softplus`, but can be any function f: R -> R^+. Defaults to exp if not explicitly specified. 
        """
        if scale_transform is None:
            scale_transform = positive(base="exp")
        self.scale_transform = scale_transform

        def conditional_distribution(Fs) -> tfp.distributions.Distribution:
            tf.debugging.assert_equal(tf.shape(Fs)[-1], 2)
            loc = Fs[..., :1]
            scale = self.scale_transform(Fs[..., 1:])
            return distribution_class(loc, scale)

        super().__init__(
            latent_dim=2, conditional_distribution=conditional_distribution, **kwargs,
        )