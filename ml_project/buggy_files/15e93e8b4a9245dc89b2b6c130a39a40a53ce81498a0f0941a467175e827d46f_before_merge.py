def _astype_nansafe(arr, dtype):
    if (np.issubdtype(arr.dtype, np.floating) and
        np.issubdtype(dtype, np.integer)):

        if np.isnan(arr).any():
            raise ValueError('Cannot convert NA to integer')

    return arr.astype(dtype)