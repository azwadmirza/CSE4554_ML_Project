    def innovation_coeff(self, seasonal_indicators: Tensor) -> Tensor:
        F = getF(seasonal_indicators)
        # seasonal_indicators = F.modulo(seasonal_indicators - 1, self.latent_dim)
        return F.one_hot(seasonal_indicators, depth=self.latent_dim()).squeeze(
            axis=2
        )