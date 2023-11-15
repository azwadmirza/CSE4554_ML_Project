    def _broadcast_indexes(self, key):
        """Prepare an indexing key for an indexing operation.

        Parameters
        -----------
        key: int, slice, array, dict or tuple of integer, slices and arrays
            Any valid input for indexing.

        Returns
        -------
        dims: tuple
            Dimension of the resultant variable.
        indexers: IndexingTuple subclass
            Tuple of integer, array-like, or slices to use when indexing
            self._data. The type of this argument indicates the type of
            indexing to perform, either basic, outer or vectorized.
        new_order : Optional[Sequence[int]]
            Optional reordering to do on the result of indexing. If not None,
            the first len(new_order) indexing should be moved to these
            positions.
        """
        key = self._item_key_to_tuple(key)  # key is a tuple
        # key is a tuple of full size
        key = indexing.expanded_indexer(key, self.ndim)
        # Convert a scalar Variable as an integer
        key = tuple([(k.data.item() if isinstance(k, Variable) and k.ndim == 0
                      else k) for k in key])
        if all(isinstance(k, BASIC_INDEXING_TYPES) for k in key):
            return self._broadcast_indexes_basic(key)

        self._validate_indexers(key)
        # Detect it can be mapped as an outer indexer
        # If all key is unlabeled, or
        # key can be mapped as an OuterIndexer.
        if all(not isinstance(k, Variable) for k in key):
            return self._broadcast_indexes_outer(key)

        # If all key is 1-dimensional and there are no duplicate labels,
        # key can be mapped as an OuterIndexer.
        dims = []
        for k, d in zip(key, self.dims):
            if isinstance(k, Variable):
                if len(k.dims) > 1:
                    return self._broadcast_indexes_vectorized(key)
                dims.append(k.dims[0])
            if not isinstance(k, integer_types):
                dims.append(d)

        if len(set(dims)) == len(dims):
            return self._broadcast_indexes_outer(key)

        return self._broadcast_indexes_vectorized(key)