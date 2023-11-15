    def log_prob(self, x: Tensor) -> Tensor:
        F = self.F

        # mask zeros for the Beta distribution input to prevent NaN gradients
        inputs = F.where(F.logical_or(x == 0, x == 1), x.zeros_like() + 0.5, x)

        # compute log density, case by case
        return F.where(
            x == 1,
            F.log(self.one_probability.broadcast_like(x)),
            F.where(
                x == 0,
                F.log(self.zero_probability.broadcast_like(x)),
                F.log(self.beta_probability)
                + self.beta_distribution.log_prob(inputs),
            ),
        )