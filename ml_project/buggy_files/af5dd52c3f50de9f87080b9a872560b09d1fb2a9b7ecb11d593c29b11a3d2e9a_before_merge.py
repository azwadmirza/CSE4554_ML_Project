    def __init__(self, prob=0.3, norm=2, lam=0.5, solver='L-BFGS-B', maxiter=10):
        """
        Create an instance of total variance minimization.

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
        """
        super(TotalVarMin, self).__init__()
        self._is_fitted = True
        self.set_params(prob=prob, norm=norm, lam=lam, solver=solver, maxiter=maxiter)