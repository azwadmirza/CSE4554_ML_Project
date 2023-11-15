    def emission_coeff(
        self, seasonal_indicators: Tensor  # (batch_size, time_length)
    ) -> Tensor:
        F = getF(seasonal_indicators)

        _emission_coeff = F.ones(shape=(1, 1, 1, self.latent_dim()))

        # get the right shape: (batch_size, seq_length, obs_dim, latent_dim)
        zeros = _broadcast_param(
            F.zeros_like(
                seasonal_indicators.slice_axis(
                    axis=-1, begin=0, end=1
                ).squeeze(axis=-1)
            ),
            axes=[2, 3],
            sizes=[1, self.latent_dim()],
        )

        return _emission_coeff.broadcast_like(zeros)