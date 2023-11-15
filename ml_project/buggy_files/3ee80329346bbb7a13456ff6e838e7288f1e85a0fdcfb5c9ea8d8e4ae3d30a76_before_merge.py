    def crit(self, prob, n):
        '''returns interpolated quantiles, similar to ppf or isf

        use two sequential 1d interpolation, first by n then by prob

        Parameters
        ----------
        prob : array_like
            probabilities corresponding to the definition of table columns
        n : int or float
            sample size, second parameter of the table

        Returns
        -------
        ppf : array_like
            critical values with same shape as prob

        '''
        prob = np.asarray(prob)
        alpha = self.alpha
        critv = self._critvals(n)

        #vectorized
        cond_ilow = (prob > alpha[0])
        cond_ihigh = (prob < alpha[-1])
        cond_interior = np.logical_or(cond_ilow, cond_ihigh)

        #scalar
        if prob.size == 1:
            if cond_interior:
                return interp1d(alpha, critv)(prob)
            else:
                return np.nan

        #vectorized
        quantile = np.nan * np.ones(prob.shape) #nans for outside
        quantile[cond_interior] = interp1d(alpha, critv)(prob[cond_interior])
        return quantile