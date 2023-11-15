    def __getitem__(self, key):
        # When getting along a single axis,
        if not isinstance(key, tuple):
            # Try to fasttrack the code through already optimized path
            try:
                return self.df.__getitem__(key)
            # This can happen if it is a list of rows
            except KeyError:
                pass
        else:
            if len(key) > self.df.ndim:
                raise IndexingError("Too many indexers")
            # If we're only slicing columns, handle the case with `__getitem__`
            if isinstance(key[0], slice) and key[0] == slice(None):
                if not isinstance(key[1], slice):
                    # Boolean indexers can just be sliced into the columns object and
                    # then passed to `__getitem__`
                    if is_boolean_array(key[1]):
                        return self.df.__getitem__(self.df.columns[key[1]])
                    return self.df.__getitem__(key[1])
                else:
                    result_slice = self.df.columns.slice_locs(key[1].start, key[1].stop)
                    return self.df.iloc[:, slice(*result_slice)]
        row_loc, col_loc, ndim, self.row_scaler, self.col_scaler = _parse_tuple(key)
        row_lookup, col_lookup = self._compute_lookup(row_loc, col_loc)
        # Check that the row_lookup/col_lookup is longer than 1 or that the
        # row_loc/col_loc is not boolean list to determine the ndim of the
        # result properly for multiindex.
        ndim = (0 if len(row_lookup) == 1 and not is_boolean_array(row_loc) else 1) + (
            0 if len(col_lookup) == 1 and not is_boolean_array(col_loc) else 1
        )
        result = super(_LocIndexer, self).__getitem__(row_lookup, col_lookup, ndim)
        # Pandas drops the levels that are in the `loc`, so we have to as well.
        if hasattr(result, "index") and isinstance(result.index, pandas.MultiIndex):
            if (
                isinstance(result, Series)
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