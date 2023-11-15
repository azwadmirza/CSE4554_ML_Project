    def __mars_tensor__(self, dtype=None, order='K'):
        return self._data.__mars_tensor__(dtype=dtype, order=order)