    def distribution(
        self,
        distr_args,
        loc: Optional[Tensor] = None,
        scale: Optional[Tensor] = None,
    ) -> NegativeBinomial:
        assert loc is None
        mu, alpha = distr_args
        if scale is None:
            return NegativeBinomial(mu, alpha)
        else:
            F = getF(mu)
            mu = F.broadcast_mul(mu, scale)
            alpha = F.broadcast_mul(alpha, F.sqrt(scale + 1.0))
            return NegativeBinomial(mu, alpha, F)