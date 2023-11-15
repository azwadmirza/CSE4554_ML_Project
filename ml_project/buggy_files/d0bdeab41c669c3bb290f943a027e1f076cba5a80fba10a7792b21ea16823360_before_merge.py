    def _transform_general(self, func, *args, **kwargs):
        """
        Transform with a non-str `func`.
        """
        klass = type(self._selected_obj)

        results = []
        for name, group in self:
            object.__setattr__(group, "name", name)
            res = func(group, *args, **kwargs)

            if isinstance(res, (DataFrame, Series)):
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