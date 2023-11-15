    def __init__(self, estimator, constraints, eps=0.01, T=50, nu=None, eta_mul=2.0):  # noqa: D103
        self._estimator = estimator
        self._constraints = constraints
        self._eps = eps
        self._T = T
        self._nu = nu
        self._eta_mul = eta_mul

        self._best_gap = None
        self._predictors = None
        self._weights = None
        self._last_t = None
        self._best_t = None
        self._n_oracle_calls = 0
        self._oracle_execution_times = None
        self._lambda_vecs = pd.DataFrame()
        self._lambda_vecs_LP = pd.DataFrame()
        self._lambda_vecs_lagrangian = pd.DataFrame()