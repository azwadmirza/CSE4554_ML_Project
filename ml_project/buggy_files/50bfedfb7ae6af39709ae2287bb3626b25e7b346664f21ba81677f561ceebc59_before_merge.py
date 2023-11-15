    def get_index(self, key):
        """Get an index for a dimension, with fall-back to a default RangeIndex
        """
        if key not in self.dims:
            raise KeyError(key)

        try:
            return self.indexes[key]
        except KeyError:
            return pd.Index(range(self.sizes[key]), name=key)