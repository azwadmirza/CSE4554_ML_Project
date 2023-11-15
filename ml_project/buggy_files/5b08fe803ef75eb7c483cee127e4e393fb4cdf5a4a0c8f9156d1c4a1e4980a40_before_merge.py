    def __init__(self, alpha, size, crit_table):
        self.alpha = np.asarray(alpha)
        self.size = np.asarray(size)
        self.crit_table = np.asarray(crit_table)

        self.n_alpha = len(alpha)
        self.signcrit = np.sign(np.diff(self.crit_table, 1).mean())
        if self.signcrit > 0: #increasing
            self.critv_bounds = self.crit_table[:,[0,1]]
        else:
            self.critv_bounds = self.crit_table[:,[1,0]]