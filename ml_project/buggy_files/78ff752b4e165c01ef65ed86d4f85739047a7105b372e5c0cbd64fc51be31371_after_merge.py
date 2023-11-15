def is_scalar(value):
    """Whether to treat a value as a scalar.

    Any non-iterable, string, or 0-D array
    """
    return (
        getattr(value, 'ndim', None) == 0 or
        isinstance(value, (basestring, bytes_type)) or not
        isinstance(value, (Iterable, ) + dask_array_type))