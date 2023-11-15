    def mean(self, axis=None, skipna=None, level=None, numeric_only=None, **kwargs):
        axis = self._get_axis_number(axis)
        data = self._validate_dtypes_sum_prod_mean(
            axis, numeric_only, ignore_axis=False
        )
        return data._reduce_dimension(
            data._query_compiler.mean(
                axis=axis,
                skipna=skipna,
                level=level,
                numeric_only=numeric_only,
                **kwargs,
            )
        )