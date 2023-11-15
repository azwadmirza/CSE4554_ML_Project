    def _callable_func(self, func, axis, *args, **kwargs):
        """Apply callable functions across given axis.

        Args:
            func: The functions to apply.
            axis: Target axis to apply the function along.

        Returns:
            A new PandasQueryCompiler.
        """
        func = wrap_udf_function(func)
        new_modin_frame = self._modin_frame._apply_full_axis(
            axis, lambda df: df.apply(func, axis=axis, *args, **kwargs)
        )
        return self.__constructor__(new_modin_frame)