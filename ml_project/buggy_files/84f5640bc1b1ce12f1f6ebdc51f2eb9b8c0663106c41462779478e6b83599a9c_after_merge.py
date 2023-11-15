def _convert_string_array(data, encoding, errors, itemsize=None):
    """
    we take a string-like that is object dtype and coerce to a fixed size
    string type

    Parameters
    ----------
    data : a numpy array of object dtype
    encoding : None or string-encoding
    errors : handler for encoding errors
    itemsize : integer, optional, defaults to the max length of the strings

    Returns
    -------
    data in a fixed-length string dtype, encoded to bytes if needed
    """

    # encode if needed
    if encoding is not None and len(data):
        data = Series(data.ravel()).str.encode(
            encoding, errors).values.reshape(data.shape)

    # create the sized dtype
    if itemsize is None:
        ensured = ensure_object(data.ravel())
        itemsize = max(1, libwriters.max_len_string_array(ensured))

    data = np.asarray(data, dtype="S%d" % itemsize)
    return data