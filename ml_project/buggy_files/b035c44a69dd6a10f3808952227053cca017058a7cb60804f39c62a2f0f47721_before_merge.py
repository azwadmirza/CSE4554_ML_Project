    def _size(self):
        return torch.Size(
            (*self.left_lazy_tensor.batch_shape, self.left_lazy_tensor.size(-2), self.right_lazy_tensor.size(-1))
        )