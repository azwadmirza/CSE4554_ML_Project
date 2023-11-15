    def _transform_general(
        self, func, *args, engine="cython", engine_kwargs=None, **kwargs
    ):
        """
        Transform with a non-str `func`.
        """
        if maybe_use_numba(engine):
            numba_func, cache_key = generate_numba_func(
                func, engine_kwargs, kwargs, "groupby_transform"
            )

        klass = type(self._selected_obj)

        results = []
        for name, group in self:
            object.__setattr__(group, "name", name)
            if maybe_use_numba(engine):
                values, index = split_for_numba(group)
                res = numba_func(values, index, *args)
                if cache_key not in NUMBA_FUNC_CACHE:
                    NUMBA_FUNC_CACHE[cache_key] = numba_func
            else:
                res = func(group, *args, **kwargs)

            if isinstance(res, (ABCDataFrame, ABCSeries)):
                res = res._values

            results.append(klass(res, index=group.index))

        # check for empty "results" to avoid concat ValueError
        if results:
            from pandas.core.reshape.concat import concat

            concatenated = concat(results)
            result = self._set_result_index_ordered(concatenated)
        else:
            result = self.obj._constructor(dtype=np.float64)
        # we will only try to coerce the result type if
        # we have a numeric dtype, as these are *always* user-defined funcs
        # the cython take a different path (and casting)
        if is_numeric_dtype(result.dtype):
            common_dtype = find_common_type([self._selected_obj.dtype, result.dtype])
            if common_dtype is result.dtype:
                result = maybe_downcast_numeric(result, self._selected_obj.dtype)

        result.name = self._selected_obj.name
        result.index = self._selected_obj.index
        return result