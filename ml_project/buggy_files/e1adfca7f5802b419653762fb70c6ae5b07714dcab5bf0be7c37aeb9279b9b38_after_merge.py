    def innovation_coeff(
        self, feature: Tensor  # (batch_size, time_length, 1)
    ) -> Tensor:
        return self.emission_coeff(feature).squeeze(axis=2)