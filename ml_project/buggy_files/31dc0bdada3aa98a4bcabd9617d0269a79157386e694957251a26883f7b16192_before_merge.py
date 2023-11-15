    def _in_memory(self):
        return (isinstance(self._data, (np.ndarray, np.number, PandasIndexAdapter)) or
                (isinstance(self._data, indexing.MemoryCachedArray) and
                 isinstance(self._data.array, np.ndarray)))