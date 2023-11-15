    def _getitem(self, row_index, col_index, *batch_indices):
        """
        Supports subindexing of the matrix this LazyTensor represents.

        The indices passed into this method will either be:
            Tensor indices
            Slices

        ..note::
            LazyTensor.__getitem__ uses this as a helper method. If you are writing your own custom LazyTensor,
            override this method rather than __getitem__ (so that you don't have to repeat the extra work)

        ..note::
            This method is used internally by the related function :func:`~gpytorch.lazy.LazyTensor.__getitem__`,
            which does some additional work. Calling this method directly is discouraged.

        This method has a number of restrictions on the type of arguments that are passed in to reduce
        the complexity of __getitem__ calls in PyTorch. In particular:
            - This method only accepts slices and tensors for the row/column indices (no ints)
            - The row and column dimensions don't dissapear (e.g. from Tensor indexing). These cases are
              handled by the `_getindices` method

        Args:
            :attr:`row_index` (slice, Tensor):
                Index for the row of the LazyTensor
            :attr:`col_index` (slice, Tensor):
                Index for the col of the LazyTensor
            :attr:`batch_indices` (tuple of slice, int, Tensor):
                Indices for the batch dimensions

        Returns:
            `LazyTensor`
        """
        # Special case: if both row and col are not indexed, then we are done
        if row_index is _noop_index and col_index is _noop_index:
            if len(batch_indices):
                components = [component[batch_indices] for component in self._args]
                res = self.__class__(*components, **self._kwargs)
                return res
            else:
                return self

        # Normal case: we have to do some processing on either the rows or columns
        # We will handle this through "interpolation"
        row_interp_indices = torch.arange(0, self.size(-2), dtype=torch.long, device=self.device).view(-1, 1)
        row_interp_indices = row_interp_indices.expand(*self.batch_shape, -1, 1)
        row_interp_values = torch.tensor(1.0, dtype=self.dtype, device=self.device).expand_as(row_interp_indices)

        col_interp_indices = torch.arange(0, self.size(-1), dtype=torch.long, device=self.device).view(-1, 1)
        col_interp_indices = col_interp_indices.expand(*self.batch_shape, -1, 1)
        col_interp_values = torch.tensor(1.0, dtype=self.dtype, device=self.device).expand_as(col_interp_indices)

        # Construct interpolated LazyTensor
        from . import InterpolatedLazyTensor

        res = InterpolatedLazyTensor(self, row_interp_indices, row_interp_values, col_interp_indices, col_interp_values)
        return res._getitem(row_index, col_index, *batch_indices)