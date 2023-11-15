    def pdtype(self) -> Optional[PandasDtype]:
        """PandasDtype of the dataframe."""
        pandas_dtype = PandasDtype.get_str_dtype(self.pandas_dtype)
        if pandas_dtype is None:
            return pandas_dtype
        return PandasDtype.from_str_alias(pandas_dtype)