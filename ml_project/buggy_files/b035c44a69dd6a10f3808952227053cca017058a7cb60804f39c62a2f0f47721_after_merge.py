    def _size(self):
        return _matmul_broadcast_shape(self.left_lazy_tensor.shape, self.right_lazy_tensor.shape)