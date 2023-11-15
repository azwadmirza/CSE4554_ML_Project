    def __call__(self, x1_, x2_=None, **params):
        x1, x2 = x1_, x2_

        if self.active_dims is not None:
            x1 = x1_.index_select(-1, self.active_dims)
            if x2_ is not None:
                x2 = x2_.index_select(-1, self.active_dims)

        if x2 is None:
            x2 = x1

        # Give x1 and x2 a last dimension, if necessary
        if x1.ndimension() == 1:
            x1 = x1.unsqueeze(1)
        if x2.ndimension() == 1:
            x2 = x2.unsqueeze(1)
        if not x1.size(-1) == x2.size(-1):
            raise RuntimeError("x1 and x2 must have the same number of dimensions!")

        return LazyEvaluatedKernelTensor(self, x1, x2)