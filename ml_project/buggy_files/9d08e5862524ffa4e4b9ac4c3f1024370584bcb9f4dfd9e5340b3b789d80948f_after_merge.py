    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        if _scipy_available and scipy.sparse.issparse(arg1):
            x = arg1.todia()
            data = x.data
            offsets = x.offsets
            shape = x.shape
            dtype = x.dtype
            copy = False
        elif isinstance(arg1, tuple):
            data, offsets = arg1
            if shape is None:
                raise ValueError('expected a shape argument')

        else:
            raise ValueError(
                'unrecognized form for dia_matrix constructor')

        data = cupy.array(data, dtype=dtype, copy=copy)
        data = cupy.atleast_2d(data)
        offsets = cupy.array(offsets, dtype='i', copy=copy)
        offsets = cupy.atleast_1d(offsets)

        if offsets.ndim != 1:
            raise ValueError('offsets array must have rank 1')

        if data.ndim != 2:
            raise ValueError('data array must have rank 2')

        if data.shape[0] != len(offsets):
            raise ValueError(
                'number of diagonals (%d) does not match the number of '
                'offsets (%d)'
                % (data.shape[0], len(offsets)))

        sorted_offsets = cupy.sort(offsets)
        if (sorted_offsets[:-1] == sorted_offsets[1:]).any():
            raise ValueError('offset array contains duplicate values')

        self.data = data
        self.offsets = offsets
        if not util.isshape(shape):
            raise ValueError('invalid shape (must be a 2-tuple of int)')
        self._shape = int(shape[0]), int(shape[1])