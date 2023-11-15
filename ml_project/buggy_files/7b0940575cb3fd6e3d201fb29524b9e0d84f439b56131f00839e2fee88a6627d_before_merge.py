    def __new__(cls, data=None, dtype=None, copy=False, name=None):
        cls._validate_dtype(dtype)

        # Coerce to ndarray if not already ndarray or Index
        if not isinstance(data, (np.ndarray, Index)):
            if is_scalar(data):
                raise cls._scalar_data_error(data)

            # other iterable of some kind
            if not isinstance(data, (ABCSeries, list, tuple)):
                data = list(data)

            data = np.asarray(data, dtype=dtype)

        if issubclass(data.dtype.type, str):
            cls._string_data_error(data)

        if copy or not is_dtype_equal(data.dtype, cls._default_dtype):
            subarr = np.array(data, dtype=cls._default_dtype, copy=copy)
            cls._assert_safe_casting(data, subarr)
        else:
            subarr = data

        if name is None and hasattr(data, "name"):
            name = data.name
        return cls._simple_new(subarr, name=name)