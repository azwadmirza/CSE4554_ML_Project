    def __getitem__(self, key):
        row_loc, col_loc, ndim, self.row_scaler, self.col_scaler = _parse_tuple(key)
        if isinstance(row_loc, slice) and row_loc == slice(None):
            # If we're only slicing columns, handle the case with `__getitem__`
            if not isinstance(col_loc, slice):
                # Boolean indexers can just be sliced into the columns object and
                # then passed to `__getitem__`
                if is_boolean_array(col_loc):
                    col_loc = self.df.columns[col_loc]
                return self.df.__getitem__(col_loc)
            else:
                result_slice = self.df.columns.slice_locs(col_loc.start, col_loc.stop)
                return self.df.iloc[:, slice(*result_slice)]

        row_lookup, col_lookup = self._compute_lookup(row_loc, col_loc)
        if any(i == -1 for i in row_lookup) or any(i == -1 for i in col_lookup):
            raise KeyError(
                "Passing list-likes to .loc or [] with any missing labels is no longer "
                "supported, see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#deprecate-loc-reindex-listlike"
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