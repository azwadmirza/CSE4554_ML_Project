    def __init__(self, arg1, shape=None, dtype=None, copy=False, blocksize=None):
        _data_matrix.__init__(self)

        if isspmatrix(arg1):
            if isspmatrix_bsr(arg1) and copy:
                arg1 = arg1.copy()
            else:
                arg1 = arg1.tobsr(blocksize=blocksize)
            self._set_self(arg1)

        elif isinstance(arg1,tuple):
            if isshape(arg1):
                # it's a tuple of matrix dimensions (M,N)
                self.shape = arg1
                M,N = self.shape
                # process blocksize
                if blocksize is None:
                    blocksize = (1,1)
                else:
                    if not isshape(blocksize):
                        raise ValueError('invalid blocksize=%s' % blocksize)
                    blocksize = tuple(blocksize)
                self.data = np.zeros((0,) + blocksize, getdtype(dtype, default=float))

                R,C = blocksize
                if (M % R) != 0 or (N % C) != 0:
                    raise ValueError('shape must be multiple of blocksize')

                # Select index dtype large enough to pass array and
                # scalar parameters to sparsetools
                idx_dtype = get_index_dtype(maxval=max(M//R, N//C, R, C))
                self.indices = np.zeros(0, dtype=idx_dtype)
                self.indptr = np.zeros(M//R + 1, dtype=idx_dtype)

            elif len(arg1) == 2:
                # (data,(row,col)) format
                from .coo import coo_matrix
                self._set_self(coo_matrix(arg1, dtype=dtype).tobsr(blocksize=blocksize))

            elif len(arg1) == 3:
                # (data,indices,indptr) format
                (data, indices, indptr) = arg1

                # Select index dtype large enough to pass array and
                # scalar parameters to sparsetools
                maxval = None
                if shape is not None:
                    maxval = max(shape)
                if blocksize is not None:
                    maxval = max(maxval, max(blocksize))
                idx_dtype = get_index_dtype((indices, indptr), maxval=maxval, check_contents=True)

                self.indices = np.array(indices, copy=copy, dtype=idx_dtype)
                self.indptr = np.array(indptr, copy=copy, dtype=idx_dtype)
                self.data = np.array(data, copy=copy, dtype=getdtype(dtype, data))
            else:
                raise ValueError('unrecognized bsr_matrix constructor usage')
        else:
            # must be dense
            try:
                arg1 = np.asarray(arg1)
            except:
                raise ValueError("unrecognized form for"
                        " %s_matrix constructor" % self.format)
            from .coo import coo_matrix
            arg1 = coo_matrix(arg1, dtype=dtype).tobsr(blocksize=blocksize)
            self._set_self(arg1)

        if shape is not None:
            self.shape = shape   # spmatrix will check for errors
        else:
            if self.shape is None:
                # shape not already set, try to infer dimensions
                try:
                    M = len(self.indptr) - 1
                    N = self.indices.max() + 1
                except:
                    raise ValueError('unable to infer matrix dimensions')
                else:
                    R,C = self.blocksize
                    self.shape = (M*R,N*C)

        if self.shape is None:
            if shape is None:
                # TODO infer shape here
                raise ValueError('need to infer shape')
            else:
                self.shape = shape

        if dtype is not None:
            self.data = self.data.astype(dtype)

        self.check_format(full_check=False)