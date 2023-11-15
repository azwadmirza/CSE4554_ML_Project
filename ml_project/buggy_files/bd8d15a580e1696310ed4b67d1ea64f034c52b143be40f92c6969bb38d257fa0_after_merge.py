    def __getitem__(self, key):
        """

        """
        if com.is_integer(key):
            return self._get_val_at(key)
        elif isinstance(key, tuple):
            data_slice = self.values[key]
        else:
            if isinstance(key, SparseArray):
                key = np.asarray(key)

            if hasattr(key, '__len__') and len(self) != len(key):
                return self.take(key)
            else:
                data_slice = self.values[key]

        return self._constructor(data_slice)