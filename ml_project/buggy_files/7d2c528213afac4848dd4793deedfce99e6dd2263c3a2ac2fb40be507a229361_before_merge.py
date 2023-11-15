    def apply(
        self,
        func,
        axis=0,
        broadcast=None,
        raw=False,
        reduce=None,
        result_type=None,
        convert_dtype=True,
        args=(),
        **kwds
    ):
        """Apply a function along input axis of DataFrame.

        Args:
            func: The function to apply
            axis: The axis over which to apply the func.
            broadcast: Whether or not to broadcast.
            raw: Whether or not to convert to a Series.
            reduce: Whether or not to try to apply reduction procedures.

        Returns:
            Series or DataFrame, depending on func.
        """
        axis = self._get_axis_number(axis)
        ErrorMessage.non_verified_udf()
        if isinstance(func, str):
            if axis == 1:
                kwds["axis"] = axis
            result = self._string_function(func, *args, **kwds)
            # Sometimes we can return a scalar here
            if isinstance(result, BasePandasDataset):
                return result._query_compiler
            return result
        elif isinstance(func, dict):
            if axis == 1:
                raise TypeError(
                    "(\"'dict' object is not callable\", "
                    "'occurred at index {0}'".format(self.index[0])
                )
            if len(self.columns) != len(set(self.columns)):
                warnings.warn(
                    "duplicate column names not supported with apply().",
                    FutureWarning,
                    stacklevel=2,
                )
        elif not callable(func) and not is_list_like(func):
            raise TypeError("{} object is not callable".format(type(func)))
        query_compiler = self._query_compiler.apply(func, axis, *args, **kwds)
        return query_compiler