    def _random(self, n, p, size=None):
        original_dtype = p.dtype
        # Set float type to float64 for numpy. This change is related to numpy issue #8317 (https://github.com/numpy/numpy/issues/8317)
        p = p.astype('float64')
        # Now, re-normalize all of the values in float64 precision. This is done inside the conditionals

        # np.random.multinomial needs `n` to be a scalar int and `p` a
        # sequence
        if p.ndim == 1 and (n.ndim == 0 or (n.ndim == 1 and n.shape[0] == 1)):
            # If `n` is already a scalar and `p` is a sequence, then just
            # return np.multinomial with some size handling
            p = p / p.sum()
            if size is not None:
                if size == p.shape:
                    size = None
                elif size[-len(p.shape):] == p.shape:
                    size = size[:len(size) - len(p.shape)]
            randnum = np.random.multinomial(n, p, size=size)
            return randnum.astype(original_dtype)
        # The shapes of `p` and `n` must be broadcasted by hand depending on
        # their ndim. We will assume that the last axis of the `p` array will
        # be the sequence to feed into np.random.multinomial. The other axis
        # will only have to be iterated over.
        if n.ndim == p.ndim:
            # p and n have the same ndim, so n.shape[-1] must be 1
            if n.shape[-1] != 1:
                raise ValueError('If n and p have the same number of '
                                 'dimensions, the last axis of n must be '
                                 'have len 1. Got {} instead.\n'
                                 'n.shape = {}\n'
                                 'p.shape = {}.'.format(n.shape[-1],
                                                        n.shape,
                                                        p.shape))
            n_p_shape = np.broadcast(np.empty(p.shape[:-1]),
                                     np.empty(n.shape[:-1])).shape
            p = np.broadcast_to(p, n_p_shape + (p.shape[-1],))
            n = np.broadcast_to(n, n_p_shape + (1,))
        elif n.ndim == p.ndim - 1:
            # n has the number of dimensions of p for the iteration, these must
            # broadcast together
            n_p_shape = np.broadcast(np.empty(p.shape[:-1]),
                                     n).shape
            p = np.broadcast_to(p, n_p_shape + (p.shape[-1],))
            n = np.broadcast_to(n, n_p_shape + (1,))
        elif p.ndim == 1:
            # p only has the sequence array. We extend it with the dimensions
            # of n
            n_p_shape = n.shape
            p = np.broadcast_to(p, n_p_shape + (p.shape[-1],))
            n = np.broadcast_to(n, n_p_shape + (1,))
        elif n.ndim == 0 or (n.dim == 1 and n.shape[0] == 1):
            # n is a scalar. We extend it with the dimensions of p
            n_p_shape = p.shape[:-1]
            n = np.broadcast_to(n, n_p_shape + (1,))
        else:
            # There is no clear rule to broadcast p and n so we raise an error
            raise ValueError('Incompatible shapes of n and p.\n'
                             'n.shape = {}\n'
                             'p.shape = {}'.format(n.shape, p.shape))

        # Check what happens with size
        if size is not None:
            if size == p.shape:
                size = None
                _size = 1
            elif size[-len(p.shape):] == p.shape:
                size = size[:len(size) - len(p.shape)]
                _size = np.prod(size)
            else:
                _size = np.prod(size)
        else:
            _size = 1

        # We now flatten p and n up to the last dimension
        p_shape = p.shape
        p = np.reshape(p, (np.prod(n_p_shape), -1))
        n = np.reshape(n, (np.prod(n_p_shape), -1))
        # We renormalize p
        p = p / p.sum(axis=1, keepdims=True)
        # We iterate calls to np.random.multinomial
        randnum = np.asarray([
            np.random.multinomial(nn, pp, size=_size)
            for (nn, pp) in zip(n, p)
        ])
        # We swap the iteration axis with the _size axis
        randnum = np.moveaxis(randnum, 1, 0)
        # We reshape the random numbers to the corresponding size + p_shape
        if size is None:
            randnum = np.reshape(randnum, p_shape)
        else:
            randnum = np.reshape(randnum, size + p_shape)
        # We cast back to the original dtype
        return randnum.astype(original_dtype)