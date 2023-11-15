    def __mars_tensor__(self, dtype=None, order='K'):
        return self._to_mars_tensor(dtype=dtype, order=order)