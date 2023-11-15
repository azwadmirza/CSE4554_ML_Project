    def reset_index(self, drop):
        if drop:
            exprs = OrderedDict()
            for c in self.columns:
                exprs[c] = self.ref(c)
            return self.__constructor__(
                columns=self.columns,
                dtypes=self._dtypes_for_exprs(exprs),
                op=TransformNode(self, exprs),
                index_cols=None,
                force_execution_mode=self._force_execution_mode,
            )
        else:
            if self._index_cols is None:
                raise NotImplementedError(
                    "default index reset with no drop is not supported"
                )
            new_columns = Index.__new__(Index, data=self._table_cols, dtype="O")
            return self.__constructor__(
                columns=new_columns,
                dtypes=self._dtypes_for_cols(None, new_columns),
                op=self._op,
                index_cols=None,
                force_execution_mode=self._force_execution_mode,
            )