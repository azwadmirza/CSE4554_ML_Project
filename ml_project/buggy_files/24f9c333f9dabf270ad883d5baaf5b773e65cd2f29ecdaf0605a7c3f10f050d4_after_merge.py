    def __init__(self, array, key=None):
        """
        Parameters
        ----------
        array : array_like
            Array like object to index.
        key : tuple, optional
            Array indexer. If provided, it is assumed to already be in
            canonical expanded form.
        """
        # We need to avoid doubly wrapping.
        if isinstance(array, type(self)):
            self.array = as_indexable(array.array)
            self.key = array.key
            if key is not None:
                self.key = self._updated_key(key)

        else:
            if key is None:
                key = (slice(None),) * array.ndim
                key = BasicIndexer(key)
            self.array = as_indexable(array)
            self.key = key