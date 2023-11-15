    def astep(self, q0, logp):
        """q0 : current state
        logp : log probability function
        """

        # Draw from the normal prior by multiplying the Cholesky decomposition
        # of the covariance with draws from a standard normal
        chol = draw_values([self.prior_chol])[0]
        nu = np.dot(chol, nr.randn(chol.shape[0]))
        y = logp(q0) - nr.standard_exponential()

        # Draw initial proposal and propose a candidate point
        theta = nr.uniform(0, 2 * np.pi)
        theta_max = theta
        theta_min = theta - 2 * np.pi
        q_new = q0 * np.cos(theta) + nu * np.sin(theta)

        while logp(q_new) <= y:
            # Shrink the bracket and propose a new point
            if theta < 0:
                theta_min = theta
            else:
                theta_max = theta
            theta = nr.uniform(theta_min, theta_max)
            q_new = q0 * np.cos(theta) + nu * np.sin(theta)

        return q_new