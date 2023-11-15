    def innovation_coeff(
        self, seasonal_indicators: Tensor  # (batch_size, time_length)
    ) -> Tensor:
        return self.emission_coeff(seasonal_indicators).squeeze(axis=2)