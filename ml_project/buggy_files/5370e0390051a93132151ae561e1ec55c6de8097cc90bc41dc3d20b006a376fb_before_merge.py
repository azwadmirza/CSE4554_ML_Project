    def _filter_is_defined(self, columns=None, negate=False):
        if columns is None:
            if sp.issparse(self.X):
                remove = (self.X.indptr[1:] !=
                          self.X.indptr[-1:] + self.X.shape[1])
            else:
                remove = bn.anynan(self.X, axis=1)
            if sp.issparse(self._Y):
                remove = np.logical_or(remove, self._Y.indptr[1:] !=
                                       self._Y.indptr[-1:] + self._Y.shape[1])
            else:
                remove = np.logical_or(remove, bn.anynan(self._Y, axis=1))
        else:
            remove = np.zeros(len(self), dtype=bool)
            for column in columns:
                col, sparse = self.get_column_view(column)
                if sparse:
                    remove = np.logical_or(remove, col == 0)
                else:
                    remove = np.logical_or(remove, bn.anynan([col], axis=0))
        retain = remove if negate else np.logical_not(remove)
        return self.from_table_rows(self, retain)