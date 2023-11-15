    def __getitem__(self, key):
        row_loc, col_loc, ndim, self.row_scaler, self.col_scaler = _parse_tuple(key)
        self._handle_enlargement(row_loc, col_loc)
        row_lookup, col_lookup = self._compute_lookup(row_loc, col_loc)
        ndim = (0 if len(row_lookup) == 1 else 1) + (0 if len(col_lookup) == 1 else 1)
        result = super(_LocIndexer, self).__getitem__(row_lookup, col_lookup, ndim)
        # Pandas drops the levels that are in the `loc`, so we have to as well.
        if hasattr(result, "index") and isinstance(result.index, pandas.MultiIndex):
            if (
                isinstance(result, pandas.Series)
                and not isinstance(col_loc, slice)
                and all(
                    col_loc[i] in result.index.levels[i] for i in range(len(col_loc))
                )
            ):
                result.index = result.index.droplevel(list(range(len(col_loc))))
            elif all(row_loc[i] in result.index.levels[i] for i in range(len(row_loc))):
                result.index = result.index.droplevel(list(range(len(row_loc))))
        if (
            hasattr(result, "columns")
            and isinstance(result.columns, pandas.MultiIndex)
            and all(col_loc[i] in result.columns.levels[i] for i in range(len(col_loc)))
        ):
            result.columns = result.columns.droplevel(list(range(len(col_loc))))
        return result