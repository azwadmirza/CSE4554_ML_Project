    def _to_mars_tensor(self, dtype=None, order='K', extract_multi_index=False):
        tensor = self._data.to_tensor(extract_multi_index=extract_multi_index)
        dtype = dtype if dtype is not None else tensor.dtype
        return tensor.astype(dtype=dtype, order=order, copy=False)