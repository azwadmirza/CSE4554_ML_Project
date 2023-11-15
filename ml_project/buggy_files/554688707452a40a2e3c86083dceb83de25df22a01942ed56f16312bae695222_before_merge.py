    def logp(self, value):
        """
        Calculate log-probability of defined Mixture distribution at specified value.

        Parameters
        ----------
        value: numeric
            Value(s) for which log-probability is calculated. If the log probabilities for multiple
            values are desired the values must be provided in a numpy array or theano tensor

        Returns
        -------
        TensorVariable
        """
        w = self.w

        return bound(logsumexp(tt.log(w) + self._comp_logp(value), axis=-1),
                     w >= 0, w <= 1, tt.allclose(w.sum(axis=-1), 1),
                     broadcast_conditions=False)