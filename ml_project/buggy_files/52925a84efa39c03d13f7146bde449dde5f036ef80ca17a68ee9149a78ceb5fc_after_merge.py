    def __init__(self, eta, n, sd_dist, *args, **kwargs):
        self.n = n
        self.eta = eta

        if 'transform' in kwargs and kwargs['transform'] is not None:
            raise ValueError('Invalid parameter: transform.')
        if 'shape' in kwargs:
            raise ValueError('Invalid parameter: shape.')

        shape = n * (n + 1) // 2

        if sd_dist.shape.ndim not in [0, 1]:
            raise ValueError('Invalid shape for sd_dist.')

        transform = transforms.CholeskyCovPacked(n)

        kwargs['shape'] = shape
        kwargs['transform'] = transform
        super().__init__(*args, **kwargs)

        self.sd_dist = sd_dist
        self.diag_idxs = transform.diag_idxs

        self.mode = floatX(np.zeros(shape))
        self.mode[self.diag_idxs] = 1