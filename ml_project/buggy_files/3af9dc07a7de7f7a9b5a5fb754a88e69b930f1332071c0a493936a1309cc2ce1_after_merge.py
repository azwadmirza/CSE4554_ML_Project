    def _reindex_columns(self, columns, copy, level, fill_value, limit=None):
        if level is not None:
            raise Exception('Reindex by level not supported for sparse')

        if com.notnull(fill_value):
            raise NotImplementedError

        if limit:
            raise NotImplementedError

        # TODO: fill value handling
        sdict = dict((k, v) for k, v in self.iteritems() if k in columns)
        return SparseDataFrame(sdict, index=self.index, columns=columns,
                               default_fill_value=self.default_fill_value)