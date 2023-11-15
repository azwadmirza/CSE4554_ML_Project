    def set_params(self, **kwargs):
        """
        Take in a dictionary of parameters and applies defence-specific checks before saving them as attributes.

        :param prob: Probability of the Bernoulli distribution.
        :type prob: `float`
        :param norm: The norm (positive integer).
        :type norm: `int`
        :param lamb: The lambda parameter in the objective function.
        :type lamb: `float`
        :param solver: Current support: L-BFGS-B, CG, Newton-CG.
        :type solver: `str`
        :param max_iter: Maximum number of iterations in an optimization.
        :type max_iter: `int`
        """
        # Save defense-specific parameters
        super(TotalVarMin, self).set_params(**kwargs)

        if not isinstance(self.prob, (float, int)) or self.prob < 0.0 or self.prob > 1.0:
            logger.error('Probability must be between 0 and 1.')
            raise ValueError('Probability must be between 0 and 1.')

        if not isinstance(self.norm, (int, np.int)) or self.norm <= 0:
            logger.error('Norm must be a positive integer.')
            raise ValueError('Norm must be a positive integer.')

        if not (self.solver == 'L-BFGS-B' or self.solver == 'CG' or self.solver == 'Newton-CG'):
            logger.error('Current support only L-BFGS-B, CG, Newton-CG.')
            raise ValueError('Current support only L-BFGS-B, CG, Newton-CG.')

        if not isinstance(self.max_iter, (int, np.int)) or self.max_iter <= 0:
            logger.error('Number of iterations must be a positive integer.')
            raise ValueError('Number of iterations must be a positive integer.')

        return True