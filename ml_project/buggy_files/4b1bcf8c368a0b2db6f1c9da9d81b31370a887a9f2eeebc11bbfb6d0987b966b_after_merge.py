    def __call__(self, x, y=None, prob=None, norm=None, lamb=None, solver=None, max_iter=None, clip_values=(0, 1)):
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
        :param lamb: The lambda parameter in the objective function.
        :type lamb: `float`
        :param solver: Current support: L-BFGS-B, CG, Newton-CG
        :type solver: `str`
        :param max_iter: Maximum number of iterations in an optimization.
        :type max_iter: `int`
        :return: similar sample
        :rtype: `np.ndarray`
        """
        params = {}
        if prob is not None:
            params['prob'] = prob

        if norm is not None:
            params['norm'] = norm

        if lamb is not None:
            params['lamb'] = lamb

        if solver is not None:
            params['solver'] = solver

        if max_iter is not None:
            params['max_iter'] = max_iter

        self.set_params(**params)
        x_ = x.copy()

        # Minimize one image at a time
        for i, xi in enumerate(x_):
            mask = (np.random.rand(xi.shape[0], xi.shape[1], xi.shape[2]) < self.prob).astype('int')
            x_[i] = self._minimize(xi, mask)

        x_ = np.clip(x_, clip_values[0], clip_values[1])

        return x_.astype(NUMPY_DTYPE)