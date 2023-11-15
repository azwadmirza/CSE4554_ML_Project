    def __new__(
        cls,
        data,
        closed=None,
        dtype=None,
        copy: bool = False,
        name=None,
        verify_integrity: bool = True,
    ):

        if name is None and hasattr(data, "name"):
            name = data.name

        with rewrite_exception("IntervalArray", cls.__name__):
            array = IntervalArray(
                data,
                closed=closed,
                copy=copy,
                dtype=dtype,
                verify_integrity=verify_integrity,
            )

        return cls._simple_new(array, name)