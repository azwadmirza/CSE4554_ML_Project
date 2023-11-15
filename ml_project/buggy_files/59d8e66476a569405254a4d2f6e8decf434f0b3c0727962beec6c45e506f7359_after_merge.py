    def inv_matmul(self, right_tensor, left_tensor=None):
        """
        Computes a linear solve (w.r.t self = :math:`A`) with several right hand sides :math:`R`.
        I.e. computes

        ... math::

            \begin{equation}
                A^{-1} R,
            \end{equation}

        where :math:`R` is :attr:`right_tensor` and :math:`A` is the LazyTensor.

        If :attr:`left_tensor` is supplied, computes

        ... math::

            \begin{equation}
                L A^{-1} R,
            \end{equation}

        where :math:`L` is :attr:`left_tensor`. Supplying this can reduce the number of
        CG calls required.

        Args:
            - :obj:`torch.tensor` (n x k) - Matrix :math:`R` right hand sides
            - :obj:`torch.tensor` (m x n) - Optional matrix :math:`L` to perform left multiplication with

        Returns:
            - :obj:`torch.tensor` - :math:`A^{-1}R` or :math:`LA^{-1}R`.
        """
        if not self.is_square:
            raise RuntimeError(
                "inv_matmul only operates on (batches of) square (positive semi-definite) LazyTensors. "
                "Got a {} of size {}.".format(self.__class__.__name__, self.size())
            )

        if self.dim() == 2 and right_tensor.dim() == 1:
            if self.shape[-1] != right_tensor.numel():
                raise RuntimeError(
                    "LazyTensor (size={}) cannot be multiplied with right-hand-side Tensor (size={}).".format(
                        self.shape, right_tensor.shape
                    )
                )

        func = InvMatmul(
            self.representation_tree(),
            has_left=(left_tensor is not None),
        )
        if left_tensor is None:
            return func(right_tensor, *self.representation())
        else:
            return func(left_tensor, right_tensor, *self.representation())