    def _expand_batch(self, batch_shape):
        return self.__class__(self.base_lazy_tensor._expand_batch(batch_shape), self._constant.expand(*batch_shape))