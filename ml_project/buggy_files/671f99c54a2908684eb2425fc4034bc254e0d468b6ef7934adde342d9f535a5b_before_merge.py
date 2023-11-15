    def kurt(self, axis=None, skipna=None, level=None, numeric_only=None, **kwargs):
        axis = self._get_axis_number(axis)
        if level is not None:
            func_kwargs = {
                "skipna": skipna,
                "level": level,
                "numeric_only": numeric_only,
            }

            return self.__constructor__(
                query_compiler=self._query_compiler.apply("kurt", axis, **func_kwargs)
            )

        if numeric_only:
            self._validate_dtypes(numeric_only=True)
        return self._reduce_dimension(
            self._query_compiler.kurt(
                axis=axis,
                skipna=skipna,
                level=level,
                numeric_only=numeric_only,
                **kwargs,
            )
        )