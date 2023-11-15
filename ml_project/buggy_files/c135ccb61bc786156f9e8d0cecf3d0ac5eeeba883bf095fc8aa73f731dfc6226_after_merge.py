def _infer_dtype(array, name=None):
    """Given an object array with no missing values, infer its dtype from its
    first element
    """
    if array.dtype.kind != 'O':
        raise TypeError('infer_type must be called on a dtype=object array')

    if array.size == 0:
        return np.dtype(float)

    element = array[(0,) * array.ndim]
    if isinstance(element, (bytes_type, unicode_type)):
        return strings.create_vlen_dtype(type(element))

    dtype = np.array(element).dtype
    if dtype.kind != 'O':
        return dtype

    raise ValueError('unable to infer dtype on variable {!r}; xarray '
                     'cannot serialize arbitrary Python objects'
                     .format(name))