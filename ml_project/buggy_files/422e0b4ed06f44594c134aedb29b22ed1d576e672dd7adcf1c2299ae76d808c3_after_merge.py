def array_encoding_disabled(array):
    """ Determine whether an array may be binary encoded.

    The NumPy array dtypes that can be encoded are:

    {binary_array_types}

    Args:
        array (np.ndarray) : the array to check

    Returns:
        bool

    """

    # disable binary encoding for non-supported dtypes
    return array.dtype not in BINARY_ARRAY_TYPES