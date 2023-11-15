    def __getitem__(self, key):
        row_loc, col_loc, ndim, self.row_scaler, self.col_scaler = _parse_tuple(key)
        self._handle_enlargement(row_loc, col_loc)
        row_lookup, col_lookup = self._compute_lookup(row_loc, col_loc)
        ndim = self._expand_dim(row_lookup, col_lookup, ndim)
        result = super(_LocIndexer, self).__getitem__(row_lookup, col_lookup, ndim)
        return result