    def _reindex_with_indexers(self, reindexers, method=None, fill_value=None,
                               limit=None, copy=False, allow_dups=False):

        if method is not None or limit is not None:
            raise NotImplementedError("cannot reindex with a method or limit "
                                      "with sparse")

        if fill_value is None:
            fill_value = np.nan

        reindexers = {self._get_axis_number(a): val
                      for (a, val) in compat.iteritems(reindexers)}

        index, row_indexer = reindexers.get(0, (None, None))
        columns, col_indexer = reindexers.get(1, (None, None))

        if columns is None:
            columns = self.columns

        new_arrays = {}
        for col in columns:
            if col not in self:
                continue
            if row_indexer is not None:
                new_arrays[col] = algos.take_1d(self[col].get_values(),
                                                row_indexer,
                                                fill_value=fill_value)
            else:
                new_arrays[col] = self[col]

        return self._constructor(new_arrays, index=index,
                                 columns=columns).__finalize__(self)