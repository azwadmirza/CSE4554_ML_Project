def np_asfarray(a, dtype=np.float64):
    # convert numba dtype types into NumPy dtype
    if isinstance(dtype, types.Type):
        dtype = as_dtype(dtype)
    if not np.issubdtype(dtype, np.inexact):
        dx = types.float64
    else:
        dx = dtype

    def impl(a, dtype=np.float64):
        return np.asarray(a, dx)
    return impl