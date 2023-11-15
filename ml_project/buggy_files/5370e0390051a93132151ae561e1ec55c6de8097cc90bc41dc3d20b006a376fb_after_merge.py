    def _filter_is_defined(self, columns=None, negate=False):
        # structure of function is obvious; pylint: disable=too-many-branches
        def _sp_anynan(a):
            return a.indptr[1:] != a[-1:] + a.shape[1]

        if columns is None:
            if sp.issparse(self.X):
                remove = _sp_anynan(self.X)
            else:
                remove = bn.anynan(self.X, axis=1)
            if sp.issparse(self._Y):
                remove += _sp_anynan(self._Y)
            else:
                remove += bn.anynan(self._Y, axis=1)
            if sp.issparse(self.metas):
                remove += _sp_anynan(self._metas)
            else:
                for i, var in enumerate(self.domain.metas):
                    col = self.metas[:, i].flatten()
                    if var.is_primitive():
                        remove += np.isnan(col.astype(float))
                    else:
                        remove += ~col.astype(bool)
        else:
            remove = np.zeros(len(self), dtype=bool)
            for column in columns:
                col, sparse = self.get_column_view(column)
                if sparse:
                    remove += col == 0
                elif self.domain[column].is_primitive():
                    remove += bn.anynan([col.astype(float)], axis=0)
                else:
                    remove += col.astype(bool)
        retain = remove if negate else np.logical_not(remove)
        return self.from_table_rows(self, retain)