    def __setitem__(self, key, value):
        pos_indexers, _ = self._remap_key(key)
        self.data_array[pos_indexers] = value