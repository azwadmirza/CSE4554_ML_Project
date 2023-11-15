def astype(data, **kwargs):
    try:
        import sparse
    except ImportError:
        sparse = None

    if (
        sparse is not None
        and isinstance(data, sparse_array_type)
        and LooseVersion(sparse.__version__) < LooseVersion("0.11.0")
        and "casting" in kwargs
    ):
        warnings.warn(
            "The current version of sparse does not support the 'casting' argument. It will be ignored in the call to astype().",
            RuntimeWarning,
            stacklevel=4,
        )
        kwargs.pop("casting")

    return data.astype(**kwargs)