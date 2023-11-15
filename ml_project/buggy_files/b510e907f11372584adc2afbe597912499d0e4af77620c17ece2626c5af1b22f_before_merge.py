def is_object_dtype(dtype):
    return np.issubdtype(dtype, np.object_) \
        or np.issubdtype(dtype, np.unicode_) \
        or np.issubdtype(dtype, np.bytes_)