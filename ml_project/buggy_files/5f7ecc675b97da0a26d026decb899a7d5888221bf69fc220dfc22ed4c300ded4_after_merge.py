    def __add__(self, other):
        """
        Return a :obj:`gpytorch.lazy.LazyTensor` that represents the sum of this lazy tensor and another matrix
        or lazy tensor.

        Args:
            :attr:`other` (:obj:`torch.tensor` or :obj:`gpytorch.lazy.LazyTensor`):
                Matrix to add to this one.

        Returns:
            :obj:`gpytorch.lazy.SumLazyTensor`:
                A sum lazy tensor representing the sum of this lazy tensor and other.
        """
        from .sum_lazy_tensor import SumLazyTensor
        from .zero_lazy_tensor import ZeroLazyTensor
        from .diag_lazy_tensor import DiagLazyTensor
        from .added_diag_lazy_tensor import AddedDiagLazyTensor
        from .non_lazy_tensor import lazify
        from torch import Tensor

        if isinstance(other, ZeroLazyTensor):
            return self
        elif isinstance(other, DiagLazyTensor):
            return AddedDiagLazyTensor(self, other)
        elif isinstance(other, Tensor):
            other = lazify(other)
            shape = _mul_broadcast_shape(self.shape, other.shape)
            new_self = self if self.shape == shape else self._expand_batch(shape[:-2])
            new_other = other if other.shape == shape else other._expand_batch(shape[:-2])
            return SumLazyTensor(new_self, new_other)
        else:
            return SumLazyTensor(self, other)