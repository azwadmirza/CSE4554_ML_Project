def _astype_nansafe(arr, dtype):
    if isinstance(dtype, basestring):
        dtype = np.dtype(dtype)

    if issubclass(arr.dtype.type, np.datetime64):
        if dtype == object:
            return lib.ints_to_pydatetime(arr.view(np.int64))
    elif (np.issubdtype(arr.dtype, np.floating) and
        np.issubdtype(dtype, np.integer)):

        if np.isnan(arr).any():
            raise ValueError('Cannot convert NA to integer')

    return arr.astype(dtype)