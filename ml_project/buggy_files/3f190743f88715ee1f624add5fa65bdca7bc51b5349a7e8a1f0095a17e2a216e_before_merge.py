    def _random(self, n, p, size=None):
        original_dtype = p.dtype
        # Set float type to float64 for numpy. This change is related to numpy issue #8317 (https://github.com/numpy/numpy/issues/8317)
        p = p.astype('float64')
        # Now, re-normalize all of the values in float64 precision. This is done inside the conditionals
        if size == p.shape:
            size = None
        if p.ndim == 1:
            p = p / p.sum()
            randnum = np.random.multinomial(n, p.squeeze(), size=size)
        elif p.ndim == 2:
            p = p / p.sum(axis=1, keepdims=True)
            randnum = np.asarray([
                np.random.multinomial(nn, pp, size=size)
                for (nn, pp) in zip(n, p)
            ])
        else:
            raise ValueError('Outcome probabilities must be 1- or 2-dimensional '
                             '(supplied `p` has {} dimensions)'.format(p.ndim))
        return randnum.astype(original_dtype)