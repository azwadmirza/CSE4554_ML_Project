    def get_issm_coeff(
        self, seasonal_indicators: Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        return (
            self.emission_coeff(seasonal_indicators),
            self.transition_coeff(seasonal_indicators),
            self.innovation_coeff(seasonal_indicators),
        )