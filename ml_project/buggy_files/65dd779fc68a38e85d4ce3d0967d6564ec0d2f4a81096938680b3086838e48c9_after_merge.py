    def crit3(self, prob, n):
        """
        Returns interpolated quantiles, similar to ppf or isf

        uses Rbf to interpolate critical values as function of `prob` and `n`

        Parameters
        ----------
        prob : array_like
            probabilities corresponding to the definition of table columns
        n : int or float
            sample size, second parameter of the table

        Returns
        -------
        ppf : array_like
            critical values with same shape as prob, returns nan for arguments
            that are outside of the table bounds

        """
        prob = np.asarray(prob)
        alpha = self.alpha

        # vectorized
        cond_ilow = (prob > alpha[0])
        cond_ihigh = (prob < alpha[-1])
        cond_interior = np.logical_or(cond_ilow, cond_ihigh)

        # scalar
        if prob.size == 1:
            if cond_interior:
                return self.polyrbf(n, prob)
            else:
                return np.nan

        # vectorized
        quantile = np.nan * np.ones(prob.shape)  # nans for outside

        quantile[cond_interior] = self.polyrbf(n, prob[cond_interior])
        return quantile