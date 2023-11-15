    def evaluate_kernel(self):
        """
        NB: This is a meta LazyTensor, in the sense that evaluate can return
        a LazyTensor if the kernel being evaluated does so.
        """
        if not self.is_batch:
            x1 = self.x1.unsqueeze(0)
            x2 = self.x2.unsqueeze(0)
        else:
            x1 = self.x1
            x2 = self.x2

        with settings.lazily_evaluate_kernels(False):
            res = self.kernel(
                x1, x2, diag=False, batch_dims=self.batch_dims, **self.params
            )
        if self.squeeze_row:
            res.squeeze_(-2)
        if self.squeeze_col:
            res.squeeze_(-1)

        if (
            not self.is_batch
            and res.ndimension() == 3
            and res.size(0) == 1
        ):
            res = res[0]

        return lazify(res)