    def get_issm_coeff(
        self, seasonal_indicators: Tensor  # (batch_size, time_length)
    ) -> Tuple[Tensor, Tensor, Tensor]:
        F = getF(seasonal_indicators)
        emission_coeff_ls, transition_coeff_ls, innovation_coeff_ls = zip(
            self.nonseasonal_issm.get_issm_coeff(seasonal_indicators),
            *[
                issm.get_issm_coeff(
                    seasonal_indicators.slice_axis(
                        axis=-1, begin=ix, end=ix + 1
                    )
                )
                for ix, issm in enumerate(self.seasonal_issms)
            ],
        )

        # stack emission and innovation coefficients
        emission_coeff = F.concat(*emission_coeff_ls, dim=-1)

        innovation_coeff = F.concat(*innovation_coeff_ls, dim=-1)

        # transition coefficient is block diagonal!
        transition_coeff = _make_block_diagonal(transition_coeff_ls)

        return emission_coeff, transition_coeff, innovation_coeff