    def compute_post_variance(self, word, chain_variance):
        """
        Based on the Variational Kalman Filtering approach for Approximate Inference [https://www.cs.princeton.edu/~blei/papers/BleiLafferty2006a.pdf]
        This function accepts the word to compute variance for, along with the associated sslm class object, and returns variance and fwd_variance
        Computes Var[\beta_{t,w}] for t = 1:T

        :math::

            fwd\_variance[t] \equiv E((beta_{t,w}-mean_{t,w})^2 |beta_{t}\ for\ 1:t) = (obs\_variance / fwd\_variance[t - 1] + chain\_variance + obs\_variance ) * (fwd\_variance[t - 1] + obs\_variance)

        :math::

            variance[t] \equiv E((beta_{t,w}-mean\_cap_{t,w})^2 |beta\_cap_{t}\ for\ 1:t) = fwd\_variance[t - 1] + (fwd\_variance[t - 1] / fwd\_variance[t - 1] + obs\_variance)^2 * (variance[t - 1] - (fwd\_variance[t-1] + obs\_variance))

        """
        INIT_VARIANCE_CONST = 1000

        T = self.num_time_slices
        variance = self.variance[word]
        fwd_variance = self.fwd_variance[word]
        # forward pass. Set initial variance very high
        fwd_variance[0] = chain_variance * INIT_VARIANCE_CONST
        for t in range(1, T + 1):
            if self.obs_variance:
                c = self.obs_variance / (fwd_variance[t - 1] + chain_variance + self.obs_variance)
            else:
                c = 0
            fwd_variance[t] = c * (fwd_variance[t - 1] + chain_variance)

        # backward pass
        variance[T] = fwd_variance[T]
        for t in range(T - 1, -1, -1):
            if fwd_variance[t] > 0.0:
                c = np.power((fwd_variance[t] / (fwd_variance[t] + chain_variance)), 2)
            else:
                c  = 0
            variance[t] = (c * (variance[t + 1] - chain_variance)) + ((1 - c) * fwd_variance[t])

        return variance, fwd_variance