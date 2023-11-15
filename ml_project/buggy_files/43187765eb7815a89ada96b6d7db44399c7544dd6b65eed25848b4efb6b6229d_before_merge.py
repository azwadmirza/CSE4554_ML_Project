    def pdtype(self) -> Optional[PandasDtype]:
        """PandasDtype of the dataframe."""
        if self.pandas_dtype is None:
            return self.pandas_dtype
        return PandasDtype.from_str_alias(
            PandasDtype.get_str_dtype(self.pandas_dtype)
        )