    def get_str_dtype(cls, pandas_dtype_arg) -> Optional[str]:
        """Get pandas-compatible string representation of dtype."""
        pandas_dtype = cls.get_dtype(pandas_dtype_arg)
        if pandas_dtype is None:
            return pandas_dtype
        elif isinstance(pandas_dtype, PandasDtype):
            return pandas_dtype.str_alias
        return str(pandas_dtype)