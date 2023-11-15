    def __mars_tensor__(self, dtype=None, order='K'):
        tensor = self._data.to_tensor()
        dtype = dtype if dtype is not None else tensor.dtype
        return tensor.astype(dtype=dtype, order=order, copy=False)