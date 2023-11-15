    def add_diag(self, added_diag):
        shape = _mul_broadcast_shape(self._diag.shape, added_diag.shape)
        return DiagLazyTensor(self._diag.expand(shape) + added_diag.expand(shape))