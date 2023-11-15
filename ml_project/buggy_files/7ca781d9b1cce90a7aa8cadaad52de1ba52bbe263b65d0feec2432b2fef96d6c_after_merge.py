    def innovation_coeff(self, feature: Tensor) -> Tensor:
        F = getF(feature)
        return F.one_hot(feature, depth=self.latent_dim()).squeeze(axis=2)