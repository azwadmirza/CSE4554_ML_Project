def _load_matrix(fin, new_format=True):
    """Load a matrix from fastText native format.

    Interprets the matrix dimensions and type from the file stream.

    Parameters
    ----------
    fin : file
        A file handle opened for reading.
    new_format : bool, optional
        True if the quant_input variable precedes
        the matrix declaration.  Should be True for newer versions of fastText.

    Returns
    -------
    :class:`numpy.array`
        The vectors as an array.
        Each vector will be a row in the array.
        The number of columns of the array will correspond to the vector size.

    """
    if new_format:
        _struct_unpack(fin, '@?')  # bool quant_input in fasttext.cc

    num_vectors, dim = _struct_unpack(fin, '@2q')

    float_size = struct.calcsize('@f')
    if float_size == 4:
        dtype = np.dtype(np.float32)
    elif float_size == 8:
        dtype = np.dtype(np.float64)
    else:
        raise ValueError("Incompatible float size: %r" % float_size)

    matrix = np.fromfile(fin, dtype=dtype, count=num_vectors * dim)
    matrix = matrix.reshape((num_vectors, dim))
    return matrix