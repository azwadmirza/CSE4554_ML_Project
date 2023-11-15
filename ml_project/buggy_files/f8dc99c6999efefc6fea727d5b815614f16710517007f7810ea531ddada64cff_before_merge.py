    def __getitem__(self, key):
        from databricks.koalas.frame import DataFrame
        from databricks.koalas.indexes import Index
        from databricks.koalas.series import Series

        def raiseNotImplemented(description):
            raise SparkPandasNotImplementedError(
                description=description,
                pandas_function=".iloc[..., ...]",
                spark_target_function="select, where")

        rows_sel, cols_sel = _unfold(key, self._ks)

        sdf = self._kdf._sdf
        if isinstance(rows_sel, Index):
            sdf_for_check_schema = sdf.select(rows_sel._scol)
            assert isinstance(sdf_for_check_schema.schema.fields[0].dataType, BooleanType), \
                (str(sdf_for_check_schema), sdf_for_check_schema.schema.fields[0].dataType)
            sdf = sdf.where(rows_sel._scol)
        elif isinstance(rows_sel, slice):
            if rows_sel == slice(None):
                # If slice is None - select everything, so nothing to do
                pass
            elif (rows_sel.start is not None) or (rows_sel.step is not None):
                raiseNotImplemented("Cannot use start or step with Spark.")
            elif not isinstance(rows_sel.stop, int):
                raise TypeError("cannot do slice indexing with these indexers [{}] of {}"
                                .format(rows_sel.stop, type(rows_sel.stop)))
            elif rows_sel.stop >= 0:
                sdf = sdf.limit(rows_sel.stop)
            else:
                sdf = sdf.limit(sdf.count() + rows_sel.stop)
        else:
            raiseNotImplemented(".iloc requires numeric slice or conditional boolean Index, "
                                "got {}".format(rows_sel))

        # make cols_sel a 1-tuple of string if a single string
        if isinstance(cols_sel, Series):
            columns = [_make_col(cols_sel)]
        elif isinstance(cols_sel, int):
            columns = [_make_col(self._kdf.columns[cols_sel])]
        elif cols_sel is None or cols_sel == slice(None):
            columns = [_make_col(col) for col in self._kdf.columns]
        elif isinstance(cols_sel, slice):
            if all(s is None or isinstance(s, int)
                   for s in (cols_sel.start, cols_sel.stop, cols_sel.step)):
                columns = [_make_col(col) for col in self._kdf.columns[cols_sel]]
            else:
                not_none = cols_sel.start if cols_sel.start is not None \
                    else cols_sel.stop if cols_sel.stop is not None else cols_sel.step
                raise TypeError('cannot do slice indexing with these indexers {} of {}'
                                .format(not_none, type(not_none)))
        elif is_list_like(cols_sel):
            if all(isinstance(s, int) for s in cols_sel):
                columns = [_make_col(col) for col in self._kdf.columns[cols_sel]]
            else:
                raise TypeError('cannot perform reduce with flexible type')
        else:
            raise ValueError("Location based indexing can only have [integer, integer slice, "
                             "listlike of integers, boolean array] types, got {}".format(cols_sel))

        try:
            kdf = DataFrame(sdf.select(self._kdf._internal.index_columns + columns))
        except AnalysisException:
            raise KeyError('[{}] don\'t exist in columns'
                           .format([col._jc.toString() for col in columns]))
        kdf._internal = kdf._internal.copy(
            data_columns=kdf._internal.data_columns[-len(columns):],
            index_map=self._kdf._internal.index_map)
        if cols_sel is not None and isinstance(cols_sel, (Series, int)):
            from databricks.koalas.series import _col
            return _col(kdf)
        else:
            return kdf