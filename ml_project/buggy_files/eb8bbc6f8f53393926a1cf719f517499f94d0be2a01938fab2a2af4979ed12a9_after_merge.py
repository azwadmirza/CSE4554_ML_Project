def _is_integer_dtype(arr):
    return (issubclass(arr.dtype.type, np.integer) and
            not arr.dtype.type == np.datetime64)