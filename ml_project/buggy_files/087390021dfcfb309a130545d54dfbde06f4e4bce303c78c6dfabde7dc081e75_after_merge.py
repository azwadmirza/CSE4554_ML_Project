    def aggregate(self, func, *args, **kwargs):
        _level = kwargs.pop("_level", None)

        relabeling = func is None and _is_multi_agg_with_relabel(**kwargs)
        if relabeling:
            func, columns, order = _normalize_keyword_aggregation(kwargs)

            kwargs = {}
        elif func is None:
            # nicer error message
            raise TypeError("Must provide 'func' or tuples of '(column, aggfunc).")

        func = _maybe_mangle_lambdas(func)

        result, how = self._aggregate(func, _level=_level, *args, **kwargs)
        if how is None:
            return result

        if result is None:

            # grouper specific aggregations
            if self.grouper.nkeys > 1:
                return self._python_agg_general(func, *args, **kwargs)
            else:

                # try to treat as if we are passing a list
                try:
                    assert not args and not kwargs
                    result = self._aggregate_multiple_funcs(
                        [func], _level=_level, _axis=self.axis
                    )

                    result.columns = Index(
                        result.columns.levels[0], name=self._selected_obj.columns.name
                    )

                    if isinstance(self.obj, SparseDataFrame):
                        # Backwards compat for groupby.agg() with sparse
                        # values. concat no longer converts DataFrame[Sparse]
                        # to SparseDataFrame, so we do it here.
                        result = SparseDataFrame(result._data)
                except Exception:
                    result = self._aggregate_generic(func, *args, **kwargs)

        if not self.as_index:
            self._insert_inaxis_grouper_inplace(result)
            result.index = np.arange(len(result))

        if relabeling:

            # used reordered index of columns
            result = result.iloc[:, order]
            result.columns = columns

        return result._convert(datetime=True)