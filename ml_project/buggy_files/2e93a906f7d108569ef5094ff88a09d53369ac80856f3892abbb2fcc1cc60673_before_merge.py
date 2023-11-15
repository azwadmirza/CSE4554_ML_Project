    def __init__(self, n, n_iter=3, train_size=.5, test_size=None,
                 random_state=None, n_bootstraps=None):
        self.n = n
        if n_bootstraps is not None:  # pragma: no cover
            warnings.warn("n_bootstraps was renamed to n_iter and will "
                          "be removed in 0.16.", DeprecationWarning)
            n_iter = n_bootstraps
        self.n_iter = n_iter
        if (isinstance(train_size, numbers.Real) and train_size >= 0.0
                and train_size <= 1.0):
            self.train_size = int(ceil(train_size * n))
        elif isinstance(train_size, numbers.Integral):
            self.train_size = train_size
        else:
            raise ValueError("Invalid value for train_size: %r" %
                             train_size)
        if self.train_size > n:
            raise ValueError("train_size=%d should not be larger than n=%d" %
                             (self.train_size, n))

        if isinstance(test_size, numbers.Real) and 0.0 <= test_size <= 1.0:
            self.test_size = int(ceil(test_size * n))
        elif isinstance(test_size, numbers.Integral):
            self.test_size = test_size
        elif test_size is None:
            self.test_size = self.n - self.train_size
        else:
            raise ValueError("Invalid value for test_size: %r" % test_size)
        if self.test_size > n:
            raise ValueError("test_size=%d should not be larger than n=%d" %
                             (self.test_size, n))

        self.random_state = random_state