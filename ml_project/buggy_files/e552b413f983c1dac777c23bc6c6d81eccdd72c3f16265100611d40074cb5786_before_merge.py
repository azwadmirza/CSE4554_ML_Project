    def transition_coeff(
        self, seasonal_indicators: Tensor  # (batch_size, time_length)
    ) -> Tensor:
        F = getF(seasonal_indicators)

        _transition_coeff = (
            (F.diag(F.ones(shape=(2,)), k=0) + F.diag(F.ones(shape=(1,)), k=1))
            .expand_dims(axis=0)
            .expand_dims(axis=0)
        )

        # get the right shape: (batch_size, seq_length, latent_dim, latent_dim)
        zeros = _broadcast_param(
            F.zeros_like(
                seasonal_indicators.slice_axis(
                    axis=-1, begin=0, end=1
                ).squeeze(axis=-1)
            ),
            axes=[2, 3],
            sizes=[self.latent_dim(), self.latent_dim()],
        )

        return _transition_coeff.broadcast_like(zeros)