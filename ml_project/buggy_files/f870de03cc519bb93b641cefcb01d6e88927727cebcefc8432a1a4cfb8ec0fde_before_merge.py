    def prob(self, x, n):
        '''find pvalues by interpolation, eiter cdf(x) or sf(x)

        returns extrem probabilities, 0.001 and 0.2, for out of range

        Parameters
        ----------
        x : array_like
            observed value, assumed to follow the distribution in the table
        n : float
            sample size, second parameter of the table

        Returns
        -------
        prob : arraylike
            This is the probability for each value of x, the p-value in
            underlying distribution is for a statistical test.

        '''
        critv = self._critvals(n)
        alpha = self.alpha
#        if self.signcrit == 1:
#            if x < critv[0]:  #generalize: ? np.sign(x - critvals[0]) == self.signcrit:
#                return alpha[0]
#            elif x > critv[-1]:
#                return alpha[-1]
#        elif self.signcrit == -1:
#            if x > critv[0]:
#                return alpha[0]
#            elif x < critv[-1]:
#                return alpha[-1]

        if self.signcrit < 1:
            #reverse if critv is decreasing
            critv, alpha = critv[::-1], alpha[::-1]

        #now critv is increasing
        if np.size(x) == 1:
            if x < critv[0]:
                return alpha[0]
            elif x > critv[-1]:
                return alpha[-1]
            return interp1d(critv, alpha)(x)[()]
        else:
            #vectorized
            cond_low = (x < critv[0])
            cond_high = (x > critv[-1])
            cond_interior = ~np.logical_or(cond_low, cond_high)

            probs = np.nan * np.ones(x.shape) #mistake if nan left
            probs[cond_low] = alpha[0]
            probs[cond_low] = alpha[-1]
            probs[cond_interior] = interp1d(critv, alpha)(x[cond_interior])

            return probs