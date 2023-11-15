    def reindex(
        self,
        index=None,
        columns=None,
        copy=True,
        **kwargs,
    ):
        if (
            kwargs.get("level") is not None
            or (index is not None and self._query_compiler.has_multiindex())
            or (columns is not None and self._query_compiler.has_multiindex(axis=1))
        ):
            if index is not None:
                kwargs["index"] = index
            if columns is not None:
                kwargs["columns"] = columns
            return self._default_to_pandas("reindex", copy=copy, **kwargs)
        new_query_compiler = None
        if index is not None:
            if not isinstance(index, pandas.Index):
                index = pandas.Index(index)
            if not index.equals(self.index):
                new_query_compiler = self._query_compiler.reindex(
                    axis=0, labels=index, **kwargs
                )
        if new_query_compiler is None:
            new_query_compiler = self._query_compiler
        final_query_compiler = None
        if columns is not None:
            if not isinstance(columns, pandas.Index):
                columns = pandas.Index(columns)
            if not columns.equals(self.columns):
                final_query_compiler = new_query_compiler.reindex(
                    axis=1, labels=columns, **kwargs
                )
        if final_query_compiler is None:
            final_query_compiler = new_query_compiler
        return self._create_or_update_from_compiler(final_query_compiler, not copy)