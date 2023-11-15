    def distribution(
        self,
        distr_args,
        loc: Optional[Tensor] = None,
        scale: Optional[Tensor] = None,
    ) -> Poisson:
        rate = distr_args
        assert loc is None
        if scale is None:
            return Poisson(rate)
        else:
            F = getF(rate)
            rate = F.broadcast_mul(rate, scale)
            return Poisson(rate, F)