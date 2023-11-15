    def _groupby_reduce(
        self, map_func, reduce_func, drop=True, numeric_only=True, **kwargs
    ):
        if self._is_multi_by or self._level is not None:
            return self._default_to_pandas(map_func, **kwargs)
        if not isinstance(self._by, type(self._query_compiler)):
            return self._apply_agg_function(map_func, drop=drop, **kwargs)

        # For aggregations, pandas behavior does this for the result.
        # For other operations it does not, so we wait until there is an aggregation to
        # actually perform this operation.
        if self._idx_name is not None and drop:
            groupby_qc = self._query_compiler.drop(columns=[self._idx_name])
        else:
            groupby_qc = self._query_compiler

        from .dataframe import DataFrame

        return DataFrame(
            query_compiler=groupby_qc.groupby_reduce(
                self._by,
                self._axis,
                self._kwargs,
                map_func,
                kwargs,
                reduce_func=reduce_func,
                reduce_args=kwargs,
                numeric_only=numeric_only,
            )
        )