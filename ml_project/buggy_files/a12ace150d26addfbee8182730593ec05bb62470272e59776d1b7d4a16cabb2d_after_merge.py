    def _reindex_index(self, index, method, copy, level, fill_value=np.nan,
                       limit=None):
        if level is not None:
            raise Exception('Reindex by level not supported for sparse')

        if self.index.equals(index):
            if copy:
                return self.copy()
            else:
                return self

        if len(self.index) == 0:
            return SparseDataFrame(index=index, columns=self.columns)

        indexer = self.index.get_indexer(index, method, limit=limit)
        indexer = com._ensure_platform_int(indexer)
        mask = indexer == -1
        need_mask = mask.any()

        new_series = {}
        for col, series in self.iteritems():
            values = series.values
            new = values.take(indexer)

            if need_mask:
                np.putmask(new, mask, fill_value)

            new_series[col] = new

        return SparseDataFrame(new_series, index=index, columns=self.columns,
                               default_fill_value=self.default_fill_value)