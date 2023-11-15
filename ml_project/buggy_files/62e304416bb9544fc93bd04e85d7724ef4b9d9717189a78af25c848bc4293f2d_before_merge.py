    def __mars_tensor__(self, dtype=None, order='K'):
        return self._data.to_tensor().astype(dtype=dtype, order=order, copy=False)