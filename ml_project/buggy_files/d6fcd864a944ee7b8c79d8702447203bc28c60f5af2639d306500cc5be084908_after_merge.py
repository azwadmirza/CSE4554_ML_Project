    def get_issm_coeff(
        self, features: Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        return (
            self.emission_coeff(features),
            self.transition_coeff(features),
            self.innovation_coeff(features),
        )