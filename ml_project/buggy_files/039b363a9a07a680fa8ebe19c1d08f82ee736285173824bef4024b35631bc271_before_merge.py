    def logp(self, value):
        """
        Calculate log-probability of TruncatedNormal distribution at specified value.

        Parameters
        ----------
        value : numeric
            Value(s) for which log-probability is calculated. If the log probabilities for multiple
            values are desired the values must be provided in a numpy array or theano tensor

        Returns
        -------
        TensorVariable
        """
        mu = self.mu
        sigma = self.sigma

        norm = self._normalization()
        logp = Normal.dist(mu=mu, sigma=sigma).logp(value) - norm

        bounds = [sigma > 0]
        if self.lower is not None:
            bounds.append(value >= self.lower)
        if self.upper is not None:
            bounds.append(value <= self.upper)
        return bound(logp, *bounds)