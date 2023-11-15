    def _random(self, n, p, size=None):
        original_dtype = p.dtype
        # Set float type to float64 for numpy. This change is related to numpy issue #8317 (https://github.com/numpy/numpy/issues/8317)
        p = p.astype('float64')
        # Now, re-normalize all of the values in float64 precision. This is done inside the conditionals
        if size == p.shape:
            size = None
        elif size[-len(p.shape):] == p.shape:
            size = size[:len(size) - len(p.shape)]

        n_dim = n.squeeze().ndim

        if (n_dim == 0) and (p.ndim == 1):
            p = p / p.sum()
            randnum = np.random.multinomial(n, p.squeeze(), size=size)
        elif (n_dim == 0) and (p.ndim > 1):
            p = p / p.sum(axis=1, keepdims=True)
            randnum = np.asarray([
                np.random.multinomial(n.squeeze(), pp, size=size)
                for pp in p
            ])
            randnum = np.moveaxis(randnum, 1, 0)
        elif (n_dim > 0) and (p.ndim == 1):
            p = p / p.sum()
            randnum = np.asarray([
                np.random.multinomial(nn, p.squeeze(), size=size)
                for nn in n
            ])
            randnum = np.moveaxis(randnum, 1, 0)
        else:
            p = p / p.sum(axis=1, keepdims=True)
            randnum = np.asarray([
                np.random.multinomial(nn, pp, size=size)
                for (nn, pp) in zip(n, p)
            ])
            randnum = np.moveaxis(randnum, 1, 0)
        return randnum.astype(original_dtype)