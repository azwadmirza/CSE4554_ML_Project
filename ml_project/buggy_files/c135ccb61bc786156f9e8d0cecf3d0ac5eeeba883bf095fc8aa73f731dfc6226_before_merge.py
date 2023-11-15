def _infer_dtype(array, name=None):
    """Given an object array with no missing values, infer its dtype from its
    first element
    """
    if array.size == 0:
        dtype = np.dtype(float)
    else:
        dtype = np.array(array[(0,) * array.ndim]).dtype
        if dtype.kind in ['S', 'U']:
            # don't just use inferred dtype to avoid truncating arrays to
            # the length of their first element
            dtype = np.dtype(dtype.kind)
        elif dtype.kind == 'O':
            raise ValueError('unable to infer dtype on variable {!r}; xarray '
                             'cannot serialize arbitrary Python objects'
                             .format(name))
    return dtype