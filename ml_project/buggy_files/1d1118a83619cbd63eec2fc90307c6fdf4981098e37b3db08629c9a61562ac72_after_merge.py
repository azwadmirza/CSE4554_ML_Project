    def _has_valid_tuple(self, key):
        """ check the key for valid keys across my indexer """
        for i, k in enumerate(key):
            if i >= self.obj.ndim:
                raise IndexingError('Too many indexers')
            try:
                self._validate_key(k, i)
            except ValueError:
                raise ValueError("Location based indexing can only have "
                                 "[{types}] types"
                                 .format(types=self._valid_types))