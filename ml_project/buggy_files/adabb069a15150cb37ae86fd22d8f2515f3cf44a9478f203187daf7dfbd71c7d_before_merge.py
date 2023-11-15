    def get_str_dtype(cls, pandas_dtype_arg):
        """Get pandas-compatible string representation of dtype."""
        dtype_ = pandas_dtype_arg
        if dtype_ is None:
            return dtype_

        if is_extension_array_dtype(dtype_):
            if isinstance(dtype_, type):
                try:
                    # Convert to str here because some pandas dtypes allow
                    # an empty constructor for compatatibility but fail on
                    # str(). e.g: PeriodDtype
                    return str(dtype_())
                except (TypeError, AttributeError) as err:
                    raise TypeError(
                        f"Pandas dtype {dtype_} cannot be instantiated: "
                        f"{err}\n Usage Tip: Use an instance or a string "
                        "representation."
                    ) from err
            return str(dtype_)

        if dtype_ in NUMPY_TYPES:
            dtype_ = cls.from_numpy_type(dtype_)
        elif isinstance(dtype_, str):
            dtype_ = cls.from_str_alias(dtype_)
        elif isinstance(dtype_, type):
            dtype_ = cls.from_python_type(dtype_)

        if isinstance(dtype_, cls):
            return dtype_.str_alias
        raise TypeError(
            "type of `pandas_dtype` argument not recognized: "
            f"{type(pandas_dtype_arg)}. Please specify a pandera PandasDtype "
            "enum, legal pandas data type, pandas data type string alias, or "
            "numpy data type string alias"
        )