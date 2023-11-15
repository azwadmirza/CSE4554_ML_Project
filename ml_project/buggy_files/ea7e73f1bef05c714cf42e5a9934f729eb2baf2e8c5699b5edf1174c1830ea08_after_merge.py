    def get_issm_coeff(
        self, features: Tensor  # (batch_size, time_length, num_features)
    ) -> Tuple[Tensor, Tensor, Tensor]:
        F = getF(features)
        emission_coeff_ls, transition_coeff_ls, innovation_coeff_ls = zip(
            *[
                issm.get_issm_coeff(
                    features.slice_axis(axis=-1, begin=ix, end=ix + 1)
                )
                for ix, issm in enumerate(
                    [self.nonseasonal_issm] + self.seasonal_issms
                )
            ],
        )

        # stack emission and innovation coefficients
        emission_coeff = F.concat(*emission_coeff_ls, dim=-1)

        innovation_coeff = F.concat(*innovation_coeff_ls, dim=-1)

        # transition coefficient is block diagonal!
        transition_coeff = _make_block_diagonal(transition_coeff_ls)

        return emission_coeff, transition_coeff, innovation_coeff