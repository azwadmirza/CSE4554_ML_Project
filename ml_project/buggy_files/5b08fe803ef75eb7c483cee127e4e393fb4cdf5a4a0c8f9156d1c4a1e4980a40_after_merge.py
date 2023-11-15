    def __init__(self, alpha, size, crit_table, asymptotic=None,
                 min_nobs=None, max_nobs=None):
        self.alpha = np.asarray(alpha)
        if self.alpha.ndim != 1:
            raise ValueError('alpha is not 1d')
        elif (np.diff(self.alpha) <= 0).any():
            raise ValueError('alpha is not sorted')
        self.size = np.asarray(size)
        if self.size.ndim != 1:
            raise ValueError('size is not 1d')
        elif (np.diff(self.size) <= 0).any():
            raise ValueError('size is not sorted')
        if self.size.ndim == 1:
            if (np.diff(alpha) <= 0).any():
                raise ValueError('alpha is not sorted')
        self.crit_table = np.asarray(crit_table)
        if self.crit_table.shape != (self.size.shape[0], self.alpha.shape[0]):
            raise ValueError('crit_table must have shape'
                             '(len(size), len(alpha))')

        self.n_alpha = len(alpha)
        self.signcrit = np.sign(np.diff(self.crit_table, 1).mean())
        if self.signcrit > 0:  # increasing
            self.critv_bounds = self.crit_table[:, [0, 1]]
        else:
            self.critv_bounds = self.crit_table[:, [1, 0]]
        self.asymptotic = None
        max_size = self.max_size = max(size)

        if asymptotic is not None:
            try:
                cv = asymptotic(self.max_size + 1)
            except Exception as exc:
                raise type(exc)('Calling asymptotic(self.size+1) failed. The '
                                'error message was:'
                                '\n\n{err_msg}'.format(err_msg=exc.args[0]))
            if len(cv) != len(alpha):
                raise ValueError('asymptotic does not return len(alpha) '
                                 'values')
            self.asymptotic = asymptotic

        self.min_nobs = max_size if min_nobs is None else min_nobs
        self.max_nobs = max_size if max_nobs is None else max_nobs
        if self.min_nobs > max_size:
            raise ValueError('min_nobs > max(size)')
        if self.max_nobs > max_size:
            raise ValueError('max_nobs > max(size)')