def is_object_dtype(dtype):
    try:
        return np.issubdtype(dtype, np.object_) \
            or np.issubdtype(dtype, np.unicode_) \
            or np.issubdtype(dtype, np.bytes_)
    except TypeError:  # pragma: no cover
        return False