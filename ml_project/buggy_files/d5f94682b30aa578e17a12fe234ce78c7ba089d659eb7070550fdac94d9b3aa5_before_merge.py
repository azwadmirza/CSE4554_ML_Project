    def _apply_text_func_elementwise(self, func, axis, *args, **kwargs):
        """Apply func passed as str across given axis in elementwise manner.

        Args:
            func: The function to apply.
            axis: Target axis to apply the function along.

        Returns:
            A new PandasQueryCompiler.
        """
        assert isinstance(func, str)
        kwargs["axis"] = axis
        new_modin_frame = self._modin_frame._apply_full_axis(
            axis, lambda df: getattr(df, func)(**kwargs)
        )
        return self.__constructor__(new_modin_frame)