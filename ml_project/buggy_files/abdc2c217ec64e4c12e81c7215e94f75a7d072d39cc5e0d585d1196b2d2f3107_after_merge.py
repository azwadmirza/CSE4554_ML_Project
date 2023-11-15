    def __init__(self, lb, ub, keep_feasible=False):
        self.lb = np.asarray(lb)
        self.ub = np.asarray(ub)
        self.keep_feasible = keep_feasible