    def __add__(self, other):
        from .diag_lazy_tensor import DiagLazyTensor
        from .added_diag_lazy_tensor import AddedDiagLazyTensor

        if isinstance(other, ZeroLazyTensor):
            return self
        elif isinstance(other, DiagLazyTensor):
            return AddedDiagLazyTensor(self, other)
        elif isinstance(other, SumLazyTensor):
            return SumLazyTensor(*(list(self.lazy_tensors) + list(other.lazy_tensors)))
        elif isinstance(other, LazyTensor):
            return SumLazyTensor(*(list(self.lazy_tensors) + [other]))
        elif isinstance(other, Tensor):
            # get broadcast shape, assuming mul broadcasting the same as add broadcasting
            broadcasted_shape = _mul_broadcast_shape(self.shape, other.shape)

            # lazify + broadcast other
            broadcasted_other = lazify(other.expand(broadcasted_shape))

            # update the lazy tensors' shape as well
            if broadcasted_shape != self.shape:
                broadcasted_lts = [
                    lt.expand(*broadcasted_shape, 1).squeeze(-1).transpose(-1, -2) for lt in self.lazy_tensors
                ]
            else:
                broadcasted_lts = list(self.lazy_tensors)

            return SumLazyTensor(*(broadcasted_lts + [broadcasted_other]))
        else:
            raise AttributeError("other must be a LazyTensor")