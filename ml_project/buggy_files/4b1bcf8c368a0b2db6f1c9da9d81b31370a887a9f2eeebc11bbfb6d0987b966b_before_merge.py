    def __call__(self, x, y=None, prob=None, norm=None, lam=None, solver=None, maxiter=None, clip_values=(0, 1)):
        """
        Apply total variance minimization to sample `x`.

        :param x: Sample to compress with shape `(batch_size, width, height, depth)`.
        :type x: `np.ndarray`
        :param y: Labels of the sample `x`. This function does not affect them in any way.
        :type y: `np.ndarray`
        :param prob: Probability of the Bernoulli distribution.
        :type prob: `float`
        :param norm: The norm (positive integer).
        :type norm: `int`
        :param lam: The lambda parameter in the objective function.
        :type lam: `float`
        :param solver: Current support: L-BFGS-B, CG, Newton-CG
        :type solver: `string`
        :param maxiter: Maximum number of iterations in an optimization.
        :type maxiter: `int`
        :return: similar sample
        :rtype: `np.ndarray`
        """
        if prob is not None:
            self.set_params(prob=prob)

        if norm is not None:
            self.set_params(norm=norm)

        if lam is not None:
            self.set_params(lam=lam)

        if solver is not None:
            self.set_params(solver=solver)

        if maxiter is not None:
            self.set_params(maxiter=maxiter)

        x_ = x.copy()

        # Minimize one image per time
        for i, xi in enumerate(x_):
            mask = (np.random.rand(xi.shape[0], xi.shape[1], xi.shape[2]) < self.prob).astype('int')
            x_[i] = self._minimize(xi, mask)

        x_ = np.clip(x_, clip_values[0], clip_values[1])

        return x_.astype(NUMPY_DTYPE)