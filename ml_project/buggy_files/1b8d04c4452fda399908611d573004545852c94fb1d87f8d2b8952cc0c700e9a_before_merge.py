    def _apply_agg_function(self, f, drop=True, **kwargs):
        """Perform aggregation and combine stages based on a given function.

        Args:
            f: The function to apply to each group.

        Returns:
             A new combined DataFrame with the result of all groups.
        """
        assert callable(f), "'{0}' object is not callable".format(type(f))
        from .dataframe import DataFrame

        if isinstance(self._by, type(self._query_compiler)):
            by = self._by.to_pandas().squeeze()
        else:
            by = self._by

        if (
            self._is_multi_by
            or self._level is not None
            or isinstance(self._index, pandas.MultiIndex)
        ):
            return self._default_to_pandas(f, **kwargs)
        # For aggregations, pandas behavior does this for the result.
        # For other operations it does not, so we wait until there is an aggregation to
        # actually perform this operation.
        if self._idx_name is not None and drop:
            groupby_qc = self._query_compiler.drop(columns=[self._idx_name])
        else:
            groupby_qc = self._query_compiler
        new_manager = groupby_qc.groupby_agg(by, self._axis, f, self._kwargs, kwargs)
        if self._idx_name is not None and self._as_index:
            new_manager.index.name = self._idx_name
        return DataFrame(query_compiler=new_manager)