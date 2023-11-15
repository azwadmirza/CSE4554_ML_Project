    def __init__(self, prob=0.3, norm=2, lamb=0.5, solver='L-BFGS-B', max_iter=10):
        """
        Create an instance of total variance minimization.

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
        """
        super(TotalVarMin, self).__init__()
        self._is_fitted = True
        self.set_params(prob=prob, norm=norm, lamb=lamb, solver=solver, max_iter=max_iter)