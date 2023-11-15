    def kalman_filter(
        self, targets: Tensor, observed: Tensor
    ) -> Tuple[Tensor, ...]:
        """
        Performs Kalman filtering given observations.


        Parameters
        ----------
        targets
            Observations, shape (batch_size, seq_length, output_dim)
        observed
            Flag tensor indicating which observations are genuine (1.0) and
            which are missing (0.0)

        Returns
        -------
        Tensor
            Log probabilities, shape (batch_size, seq_length)
        Tensor
            Mean of p(l_T | l_{T-1}), where T is seq_length, with shape
            (batch_size, latent_dim)
        Tensor
            Covariance of p(l_T | l_{T-1}), where T is seq_length, with shape
            (batch_size, latent_dim, latent_dim)
        """
        F = self.F
        # targets[t]: (batch_size, obs_dim)
        targets = targets.split(
            axis=1, num_outputs=self.seq_length, squeeze_axis=True
        )

        log_p_seq = []

        mean = self.prior_mean
        cov = self.prior_cov

        observed = (
            observed.split(
                axis=1, num_outputs=self.seq_length, squeeze_axis=True
            )
            if observed is not None
            else None
        )

        for t in range(self.seq_length):
            # Compute the filtered distribution
            #   p(l_t | z_1, ..., z_{t + 1})
            # and log - probability
            #   log p(z_t | z_0, z_{t - 1})
            filtered_mean, filtered_cov, log_p = kalman_filter_step(
                F,
                target=targets[t],
                prior_mean=mean,
                prior_cov=cov,
                emission_coeff=self.emission_coeff[t],
                residual=self.residuals[t],
                noise_std=self.noise_std[t],
                latent_dim=self.latent_dim,
                output_dim=self.output_dim,
            )

            log_p_seq.append(log_p.expand_dims(axis=1))

            # Mean of p(l_{t+1} | l_t)
            mean = F.linalg_gemm2(
                self.transition_coeff[t],
                (
                    filtered_mean.expand_dims(axis=-1)
                    if observed is None
                    else F.where(
                        observed[t], x=filtered_mean, y=mean
                    ).expand_dims(axis=-1)
                ),
            ).squeeze(axis=-1)

            # Covariance of p(l_{t+1} | l_t)
            cov = F.linalg_gemm2(
                self.transition_coeff[t],
                F.linalg_gemm2(
                    (
                        filtered_cov
                        if observed is None
                        else F.where(observed[t], x=filtered_cov, y=cov)
                    ),
                    self.transition_coeff[t],
                    transpose_b=True,
                ),
            ) + F.linalg_gemm2(
                self.innovation_coeff[t],
                self.innovation_coeff[t],
                transpose_a=True,
            )

        # Return sequence of log likelihoods, as well as
        # final mean and covariance of p(l_T | l_{T-1} where T is seq_length
        return F.concat(*log_p_seq, dim=1), mean, cov