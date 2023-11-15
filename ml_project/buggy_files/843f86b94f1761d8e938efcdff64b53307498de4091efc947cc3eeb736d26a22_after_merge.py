    def _size(self):
        return _mul_broadcast_shape(*[lt.shape for lt in self.lazy_tensors])