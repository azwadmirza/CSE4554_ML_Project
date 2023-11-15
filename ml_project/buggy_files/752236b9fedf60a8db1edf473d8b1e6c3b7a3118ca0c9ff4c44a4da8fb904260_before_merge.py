    def _callable_func(self, func, axis, *args, **kwargs):
        """Apply callable functions across given axis.

        Args:
            func: The functions to apply.
            axis: Target axis to apply the function along.

        Returns:
            A new PandasQueryCompiler.
        """
        if isinstance(pandas.DataFrame().apply(func), pandas.Series):
            new_modin_frame = self._modin_frame._fold_reduce(
                axis, lambda df: df.apply(func, axis=axis, *args, **kwargs)
            )
        else:
            new_modin_frame = self._modin_frame._apply_full_axis(
                axis, lambda df: df.apply(func, axis=axis, *args, **kwargs)
            )
        return self.__constructor__(new_modin_frame)