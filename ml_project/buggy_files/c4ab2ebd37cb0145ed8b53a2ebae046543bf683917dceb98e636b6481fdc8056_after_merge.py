    def _unpack_index(self, index):
        """ Parse index. Always return a tuple of the form (row, col).
        Where row/col is a integer, slice, or array of integers.
        """
        # First, check if indexing with single boolean matrix.
        from .base import spmatrix  # This feels dirty but...
        if (isinstance(index, (spmatrix, np.ndarray)) and
           (index.ndim == 2) and index.dtype.kind == 'b'):
                return index.nonzero()

        # Parse any ellipses.
        index = self._check_ellipsis(index)

        # Next, parse the tuple or object
        if isinstance(index, tuple):
            if len(index) == 2:
                row, col = index
            elif len(index) == 1:
                row, col = index[0], slice(None)
            else:
                raise IndexError('invalid number of indices')
        else:
            row, col = index, slice(None)

        # Next, check for validity, or transform the index as needed.
        row, col = self._check_boolean(row, col)
        return row, col