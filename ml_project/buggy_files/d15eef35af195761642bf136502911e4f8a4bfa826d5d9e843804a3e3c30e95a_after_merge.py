    def __getitem__(self, key):
        from databricks.koalas.frame import DataFrame
        from databricks.koalas.series import Series

        def raiseNotImplemented(description):
            raise SparkPandasNotImplementedError(
                description=description,
                pandas_function=".loc[..., ...]",
                spark_target_function="select, where")

        rows_sel, cols_sel = _unfold(key, self._ks)

        sdf = self._kdf._sdf
        if isinstance(rows_sel, Series):
            sdf_for_check_schema = sdf.select(rows_sel._scol)
            assert isinstance(sdf_for_check_schema.schema.fields[0].dataType, BooleanType), \
                (str(sdf_for_check_schema), sdf_for_check_schema.schema.fields[0].dataType)
            sdf = sdf.where(rows_sel._scol)
        elif isinstance(rows_sel, slice):
            if rows_sel.step is not None:
                raiseNotImplemented("Cannot use step with Spark.")
            if rows_sel == slice(None):
                # If slice is None - select everything, so nothing to do
                pass
            elif len(self._kdf._internal.index_columns) == 0:
                raiseNotImplemented("Cannot use slice for Spark if no index provided.")
            elif len(self._kdf._internal.index_columns) == 1:
                start = rows_sel.start
                stop = rows_sel.stop

                index_column = self._kdf.index.to_series()
                index_data_type = index_column.schema[0].dataType
                cond = []
                if start is not None:
                    cond.append(index_column._scol >= F.lit(start).cast(index_data_type))
                if stop is not None:
                    cond.append(index_column._scol <= F.lit(stop).cast(index_data_type))

                if len(cond) > 0:
                    sdf = sdf.where(reduce(lambda x, y: x & y, cond))
            else:
                raiseNotImplemented("Cannot use slice for MultiIndex with Spark.")
        elif isinstance(rows_sel, str):
            raiseNotImplemented("Cannot use a scalar value for row selection with Spark.")
        else:
            try:
                rows_sel = list(rows_sel)
            except TypeError:
                raiseNotImplemented("Cannot use a scalar value for row selection with Spark.")
            if len(rows_sel) == 0:
                sdf = sdf.where(F.lit(False))
            elif len(self._kdf._internal.index_columns) == 1:
                index_column = self._kdf.index.to_series()
                index_data_type = index_column.schema[0].dataType
                if len(rows_sel) == 1:
                    sdf = sdf.where(
                        index_column._scol == F.lit(rows_sel[0]).cast(index_data_type))
                else:
                    sdf = sdf.where(index_column._scol.isin(
                        [F.lit(r).cast(index_data_type) for r in rows_sel]))
            else:
                raiseNotImplemented("Cannot select with MultiIndex with Spark.")

        # make cols_sel a 1-tuple of string if a single string
        if isinstance(cols_sel, (str, Series)):
            cols_sel = _make_col(cols_sel)
        elif isinstance(cols_sel, slice) and cols_sel != slice(None):
            raise raiseNotImplemented("Can only select columns either by name or reference or all")
        elif isinstance(cols_sel, slice) and cols_sel == slice(None):
            cols_sel = None

        if cols_sel is None:
            columns = self._kdf._internal.data_scols
        elif isinstance(cols_sel, spark.Column):
            columns = [cols_sel]
        else:
            columns = [_make_col(c) for c in cols_sel]
        try:
            kdf = DataFrame(sdf.select(self._kdf._internal.index_scols + columns))
        except AnalysisException:
            raise KeyError('[{}] don\'t exist in columns'
                           .format([col._jc.toString() for col in columns]))
        kdf._internal = kdf._internal.copy(
            data_columns=kdf._internal.data_columns[-len(columns):],
            index_map=self._kdf._internal.index_map)
        if cols_sel is not None and isinstance(cols_sel, spark.Column):
            from databricks.koalas.series import _col
            return _col(kdf)
        else:
            return kdf