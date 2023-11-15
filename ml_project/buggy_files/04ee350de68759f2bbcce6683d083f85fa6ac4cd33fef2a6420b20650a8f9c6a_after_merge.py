    def __getitem__(self, key):
        if callable(key):
            return self.__getitem__(key(self.df))
        row_loc, col_loc, ndim, self.row_scaler, self.col_scaler = _parse_tuple(key)
        self._check_dtypes(row_loc)
        self._check_dtypes(col_loc)

        row_lookup, col_lookup = self._compute_lookup(row_loc, col_loc)
        result = super(_iLocIndexer, self).__getitem__(row_lookup, col_lookup, ndim)
        if isinstance(result, Series):
            result._parent = self.df
            result._parent_axis = 0
        return result