    def log_prob(self, x: Tensor) -> Tensor:
        F = self.F
        alpha, beta = self.alpha, self.beta

        def gamma_log_prob(x, alpha, beta):
            return (
                alpha * F.log(beta)
                - F.gammaln(alpha)
                + (alpha - 1) * F.log(x)
                - beta * x
            )

        """
        The gamma_log_prob(x) above returns NaNs for x<=0. Wherever there are NaN in either of the F.where() conditional
        vectors, then F.where() returns NaN at that entry as well, due to its indicator function multiplication: 
        1*f(x) + np.nan*0 = nan, since np.nan*0 return nan. 
        Therefore replacing gamma_log_prob(x) with gamma_log_prob(abs(x) mitigates nan returns in cases of x<=0 without 
        altering the value in cases of x>0. 
        This is a known issue in pytorch as well https://github.com/pytorch/pytorch/issues/12986.
        """
        # mask zeros to prevent NaN gradients for x==0
        x_masked = F.where(x == 0, x.ones_like() * 0.5, x)

        return F.where(
            x > 0,
            gamma_log_prob(F.abs(x_masked), alpha, beta),
            -np.inf * F.ones_like(x),
        )