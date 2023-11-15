    def __new__(
        cls,
        data=None,
        categories=None,
        ordered=None,
        dtype=None,
        copy=False,
        name=None,
    ):

        dtype = CategoricalDtype._from_values_or_dtype(data, categories, ordered, dtype)

        name = maybe_extract_name(name, data, cls)

        if not is_categorical_dtype(data):
            # don't allow scalars
            # if data is None, then categories must be provided
            if is_scalar(data):
                if data is not None or categories is None:
                    raise cls._scalar_data_error(data)
                data = []

        data = cls._create_categorical(data, dtype=dtype)

        data = data.copy() if copy else data

        return cls._simple_new(data, name=name)