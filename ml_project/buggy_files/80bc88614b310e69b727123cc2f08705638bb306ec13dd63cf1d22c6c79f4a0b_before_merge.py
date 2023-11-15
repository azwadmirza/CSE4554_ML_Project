    def __getitem__(self, key):
        """

        """
        if com.is_integer(key):
            return self._get_val_at(key)
        else:
            if isinstance(key, SparseArray):
                key = np.asarray(key)
            if hasattr(key, '__len__') and len(self) != len(key):
                indices = self.sp_index
                if hasattr(indices, 'to_int_index'):
                    indices = indices.to_int_index()
                data_slice = self.values.take(indices.indices)[key]
            else:
                data_slice = self.values[key]
            return self._constructor(data_slice)