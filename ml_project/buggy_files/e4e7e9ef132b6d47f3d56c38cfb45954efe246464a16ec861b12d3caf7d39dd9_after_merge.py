    def emission_coeff(
        self, feature: Tensor  # (batch_size, time_length, 1)
    ) -> Tensor:
        F = getF(feature)

        _emission_coeff = F.ones(shape=(1, 1, 1, self.latent_dim()))

        # get the right shape: (batch_size, time_length, obs_dim, latent_dim)
        zeros = _broadcast_param(
            feature.squeeze(axis=2),
            axes=[2, 3],
            sizes=[1, self.latent_dim()],
        )

        return _emission_coeff.broadcast_like(zeros)