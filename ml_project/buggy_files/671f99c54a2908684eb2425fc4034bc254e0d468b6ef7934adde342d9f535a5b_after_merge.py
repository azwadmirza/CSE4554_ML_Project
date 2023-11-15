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

        if numeric_only is not None and not numeric_only:
            self._validate_dtypes(numeric_only=True)

        data = self._get_numeric_data(axis) if numeric_only else self

        return self._reduce_dimension(
            data._query_compiler.kurt(
                axis=axis,
                skipna=skipna,
                level=level,
                numeric_only=numeric_only,
                **kwargs,
            )
        )