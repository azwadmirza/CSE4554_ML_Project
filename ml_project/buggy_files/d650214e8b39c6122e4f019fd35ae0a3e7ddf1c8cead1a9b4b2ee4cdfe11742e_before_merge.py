    def emission_coeff(self, seasonal_indicators: Tensor) -> Tensor:
        F = getF(seasonal_indicators)
        return F.one_hot(seasonal_indicators, depth=self.latent_dim())