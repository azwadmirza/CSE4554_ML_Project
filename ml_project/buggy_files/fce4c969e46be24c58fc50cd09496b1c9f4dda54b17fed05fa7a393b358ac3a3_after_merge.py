    def forward(self, x1, x2, **params):
        """
        Computes the covariance between x1 and x2.
        This method should be imlemented by all Kernel subclasses.

        .. note::

            All non-compositional kernels should use the :meth:`gpytorch.kernels.Kernel._create_input_grid`
            method to create a meshgrid between x1 and x2 (if necessary).

            Do not manually create the grid - this is inefficient and will cause erroneous behavior in certain
            evaluation modes.

        Args:
            :attr:`x1` (Tensor `n x d` or `b x n x d`)
            :attr:`x2` (Tensor `m x d` or `b x m x d`) - for diag mode, these must be the same inputs

        Returns:
            :class:`Tensor` or :class:`gpytorch.lazy.LazyTensor`.
            The exact size depends on the kernel's evaluation mode:

            * `full_covar`: `n x m` or `b x n x m`
            * `full_covar` with `dim_groups=k`: `k x n x m` or `b x k x n x m`
            * `diag`: `n` or `b x n`
            * `diag` with `dim_groups=k`: `k x n` or `b x k x n`
        """
        raise NotImplementedError()