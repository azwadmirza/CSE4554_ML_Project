    def __setitem__(self, key, value):
        _, N, K = self.shape
        if isinstance(value, DataFrame):
            value = value.reindex(index=self.major_axis,
                                  columns=self.minor_axis)
            mat = value.values
        elif isinstance(value, np.ndarray):
            assert(value.shape == (N, K))
            mat = np.asarray(value)
        elif np.isscalar(value):
            dtype = _infer_dtype(value)
            mat = np.empty((N, K), dtype=dtype)
            mat.fill(value)
        else:
            raise TypeError('Cannot set item of type: %s' % str(type(value)))

        mat = mat.reshape((1, N, K))
        NDFrame._set_item(self, key, mat)