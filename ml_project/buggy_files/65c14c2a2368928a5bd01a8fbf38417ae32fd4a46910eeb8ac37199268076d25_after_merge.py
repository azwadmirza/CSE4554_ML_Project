    def reindex(
        self,
        labels=None,
        index=None,
        columns=None,
        axis=None,
        method=None,
        copy=True,
        level=None,
        fill_value=np.nan,
        limit=None,
        tolerance=None,
    ):
        axis = self._get_axis_number(axis)
        if (columns is not None and self._query_compiler.has_multiindex(axis=1)) or (
            index is not None and self._query_compiler.has_multiindex()
        ):
            return self._default_to_pandas(
                "reindex",
                labels=labels,
                index=index,
                columns=columns,
                method=method,
                copy=copy,
                level=level,
                fill_value=fill_value,
                limit=limit,
                tolerance=tolerance,
            )
        if (
            level is not None
            or (axis == 1 and self._query_compiler.has_multiindex(axis=1))
            or (axis == 0 and self._query_compiler.has_multiindex())
        ):
            return self._default_to_pandas(
                "reindex",
                labels=labels,
                level=level,
                method=method,
                copy=copy,
                axis=axis,
                fill_value=fill_value,
                limit=limit,
                tolerance=tolerance,
            )
        if axis == 0 and labels is not None:
            index = labels
        elif labels is not None:
            columns = labels
        new_query_compiler = None
        if index is not None:
            if not isinstance(index, pandas.Index):
                index = pandas.Index(index)
            if not index.equals(self.index):
                new_query_compiler = self._query_compiler.reindex(
                    axis=0,
                    labels=index,
                    method=method,
                    fill_value=fill_value,
                    limit=limit,
                    tolerance=tolerance,
                )
        if new_query_compiler is None:
            new_query_compiler = self._query_compiler
        final_query_compiler = None
        if columns is not None:
            if not isinstance(columns, pandas.Index):
                columns = pandas.Index(columns)
            if not columns.equals(self.columns):
                final_query_compiler = new_query_compiler.reindex(
                    axis=1,
                    labels=columns,
                    method=method,
                    fill_value=fill_value,
                    limit=limit,
                    tolerance=tolerance,
                )
        if final_query_compiler is None:
            final_query_compiler = new_query_compiler
        return self._create_or_update_from_compiler(final_query_compiler, not copy)