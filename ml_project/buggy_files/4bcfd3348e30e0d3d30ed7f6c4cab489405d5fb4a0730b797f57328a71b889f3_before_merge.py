    def sample(
        self, num_samples: Optional[int] = None, scale: Optional[Tensor] = None
    ) -> Tensor:
        r"""
        Generates samples from the LDS: p(z_1, z_2, \ldots, z_{`seq_length`}).

        Parameters
        ----------
        num_samples
            Number of samples to generate
        scale
            Scale of each sequence in x, shape (batch_size, output_dim)

        Returns
        -------
        Tensor
            Samples, shape (num_samples, batch_size, seq_length, output_dim)
        """
        F = self.F

        # Note on shapes: here we work with tensors of the following shape
        # in each time step t: (num_samples, batch_size, dim, dim),
        # where dim can be obs_dim or latent_dim or a constant 1 to facilitate
        # generalized matrix multiplication (gemm2)

        # Sample observation noise for all time steps
        # noise_std: (batch_size, seq_length, obs_dim, 1)
        noise_std = F.stack(*self.noise_std, axis=1).expand_dims(axis=-1)

        # samples_eps_obs[t]: (num_samples, batch_size, obs_dim, 1)
        samples_eps_obs = (
            Gaussian(noise_std.zeros_like(), noise_std)
            .sample(num_samples)
            .split(axis=-3, num_outputs=self.seq_length, squeeze_axis=True)
        )

        # Sample standard normal for all time steps
        # samples_eps_std_normal[t]: (num_samples, batch_size, obs_dim, 1)
        samples_std_normal = (
            Gaussian(noise_std.zeros_like(), noise_std.ones_like())
            .sample(num_samples)
            .split(axis=-3, num_outputs=self.seq_length, squeeze_axis=True)
        )

        # Sample the prior state.
        # samples_lat_state: (num_samples, batch_size, latent_dim, 1)
        # The prior covariance is observed to be slightly negative definite whenever there is
        # excessive zero padding at the beginning of the time series.
        # We add positive tolerance to the diagonal to avoid numerical issues.
        # Note that `jitter_cholesky` adds positive tolerance only if the decomposition without jitter fails.
        state = MultivariateGaussian(
            self.prior_mean,
            jitter_cholesky(
                F, self.prior_cov, self.latent_dim, float_type=np.float32
            ),
        )
        samples_lat_state = state.sample(num_samples).expand_dims(axis=-1)

        samples_seq = []
        for t in range(self.seq_length):
            # Expand all coefficients to include samples in axis 0
            # emission_coeff_t: (num_samples, batch_size, obs_dim, latent_dim)
            # transition_coeff_t:
            #   (num_samples, batch_size, latent_dim, latent_dim)
            # innovation_coeff_t: (num_samples, batch_size, 1, latent_dim)
            emission_coeff_t, transition_coeff_t, innovation_coeff_t = [
                _broadcast_param(coeff, axes=[0], sizes=[num_samples])
                if num_samples is not None
                else coeff
                for coeff in [
                    self.emission_coeff[t],
                    self.transition_coeff[t],
                    self.innovation_coeff[t],
                ]
            ]

            # Expand residuals as well
            # residual_t: (num_samples, batch_size, obs_dim, 1)
            residual_t = (
                _broadcast_param(
                    self.residuals[t].expand_dims(axis=-1),
                    axes=[0],
                    sizes=[num_samples],
                )
                if num_samples is not None
                else self.residuals[t].expand_dims(axis=-1)
            )

            # (num_samples, batch_size, 1, obs_dim)
            samples_t = (
                F.linalg_gemm2(emission_coeff_t, samples_lat_state)
                + residual_t
                + samples_eps_obs[t]
            )
            samples_t = (
                samples_t.swapaxes(dim1=2, dim2=3)
                if num_samples is not None
                else samples_t.swapaxes(dim1=1, dim2=2)
            )
            samples_seq.append(samples_t)

            # sample next state: (num_samples, batch_size, latent_dim, 1)
            samples_lat_state = F.linalg_gemm2(
                transition_coeff_t, samples_lat_state
            ) + F.linalg_gemm2(
                innovation_coeff_t, samples_std_normal[t], transpose_a=True
            )

        # (num_samples, batch_size, seq_length, obs_dim)
        samples = F.concat(*samples_seq, dim=-2)
        return (
            samples
            if scale is None
            else F.broadcast_mul(
                samples,
                scale.expand_dims(axis=1).expand_dims(axis=0)
                if num_samples is not None
                else scale.expand_dims(axis=1),
            )
        )