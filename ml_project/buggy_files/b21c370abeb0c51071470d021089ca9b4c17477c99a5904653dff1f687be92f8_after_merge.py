    def __init__(self, n, p, *args, **kwargs):
        super(Multinomial, self).__init__(*args, **kwargs)

        p = p / tt.sum(p, axis=-1, keepdims=True)
        n = np.squeeze(n) # works also if n is a tensor

        if len(self.shape) > 1:
            m = self.shape[-2]
            try:
                assert n.shape == (m,)
            except (AttributeError, AssertionError):
                n = n * tt.ones(m)
            self.n = tt.shape_padright(n)
            self.p = p if p.ndim > 1 else tt.shape_padleft(p)
        elif n.ndim == 1:
            self.n = tt.shape_padright(n)
            self.p = p if p.ndim > 1 else tt.shape_padleft(p)
        else:
            # n is a scalar, p is a 1d array
            self.n = tt.as_tensor_variable(n)
            self.p = tt.as_tensor_variable(p)

        self.mean = self.n * self.p
        mode = tt.cast(tt.round(self.mean), 'int32')
        diff = self.n - tt.sum(mode, axis=-1, keepdims=True)
        inc_bool_arr = tt.abs_(diff) > 0
        mode = tt.inc_subtensor(mode[inc_bool_arr.nonzero()],
                                diff[inc_bool_arr.nonzero()])
        self.mode = mode