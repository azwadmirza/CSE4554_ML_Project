    def get_index(self, key):
        """Get an index for a dimension, with fall-back to a default RangeIndex
        """
        if key not in self.dims:
            raise KeyError(key)

        try:
            return self.indexes[key]
        except KeyError:
            # need to ensure dtype=int64 in case range is empty on Python 2
            return pd.Index(range(self.sizes[key]), name=key, dtype=np.int64)