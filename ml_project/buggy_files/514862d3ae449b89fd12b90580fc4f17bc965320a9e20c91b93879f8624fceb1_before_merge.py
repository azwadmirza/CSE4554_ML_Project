    def sort_rows(self, columns, ascending, ignore_index, na_position):
        if na_position != "first" and na_position != "last":
            raise ValueError(f"Unsupported na_position value '{na_position}'")

        if not isinstance(columns, list):
            columns = [columns]

        for col in columns:
            if col not in self._table_cols:
                raise ValueError(f"Unknown column '{col}'")

        if isinstance(ascending, list):
            if len(ascending) != len(columns):
                raise ValueError("ascending list length doesn't match columns list")
        else:
            if not isinstance(ascending, bool):
                raise ValueError("unsupported ascending value")
            ascending = [ascending] * len(columns)

        if ignore_index:
            # If index is ignored then we might need to drop some columns.
            # At the same time some of dropped index columns can be used
            # for sorting and should be droped after sorting is done.
            if self._index_cols is not None:
                base = self

                drop_index_cols_before = [
                    col for col in self._index_cols if col not in columns
                ]
                drop_index_cols_after = [
                    col for col in self._index_cols if col in columns
                ]
                if not drop_index_cols_after:
                    drop_index_cols_after = None

                if drop_index_cols_before:
                    exprs = OrderedDict()
                    index_cols = (
                        drop_index_cols_after if drop_index_cols_after else None
                    )
                    for col in drop_index_cols_after:
                        exprs[col] = base.ref(col)
                    for col in base.columns:
                        exprs[col] = base.ref(col)
                    base = self.__constructor__(
                        columns=base.columns,
                        dtypes=self._dtypes_for_exprs(exprs),
                        op=TransformNode(base, exprs),
                        index_cols=index_cols,
                        force_execution_mode=self._force_execution_mode,
                    )

                base = self.__constructor__(
                    columns=base.columns,
                    dtypes=base._dtypes,
                    op=SortNode(base, columns, ascending, na_position),
                    index_cols=base._index_cols,
                    force_execution_mode=self._force_execution_mode,
                )

                if drop_index_cols_after:
                    exprs = OrderedDict()
                    for col in base.columns:
                        exprs[col] = base.ref(col)
                    base = self.__constructor__(
                        columns=base.columns,
                        dtypes=self._dtypes_for_exprs(exprs),
                        op=TransformNode(base, exprs),
                        index_cols=None,
                        force_execution_mode=self._force_execution_mode,
                    )

                return base
            else:
                return self.__constructor__(
                    columns=self.columns,
                    dtypes=self._dtypes,
                    op=SortNode(self, columns, ascending, na_position),
                    index_cols=None,
                    force_execution_mode=self._force_execution_mode,
                )
        else:
            base = self

            # If index is preserved and we have no index columns then we
            # need to create one using __rowid__ virtual column.
            if self._index_cols is None:
                base = base._materialize_rowid()

            return self.__constructor__(
                columns=base.columns,
                dtypes=base._dtypes,
                op=SortNode(base, columns, ascending, na_position),
                index_cols=base._index_cols,
                force_execution_mode=self._force_execution_mode,
            )