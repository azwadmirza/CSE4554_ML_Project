    def to_numpy(self, dtype=None, copy=False, na_value=lib.no_default):
        array = np.asarray(self._arrow_array.to_pandas())
        if copy or na_value is not lib.no_default:
            array = array.copy()
        if na_value is not lib.no_default:
            array[self.isna()] = na_value
        return array