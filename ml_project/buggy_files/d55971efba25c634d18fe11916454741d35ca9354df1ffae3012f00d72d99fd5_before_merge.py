def array_repr(arr, max_line_width=None, precision=None, suppress_small=None):
    """
    Return the string representation of an array.

    Parameters
    ----------
    arr : ndarray
        Input array.
    max_line_width : int, optional
        The maximum number of columns the string should span. Newline
        characters split the string appropriately after array elements.
    precision : int, optional
        Floating point precision. Default is the current printing precision
        (usually 8), which can be altered using `set_printoptions`.
    suppress_small : bool, optional
        Represent very small numbers as zero, default is False. Very small
        is defined by `precision`, if the precision is 8 then
        numbers smaller than 5e-9 are represented as zero.

    Returns
    -------
    string : str
      The string representation of an array.

    See Also
    --------
    array_str, array2string, set_printoptions

    Examples
    --------
    >>> np.array_repr(np.array([1,2]))
    'array([1, 2])'
    >>> np.array_repr(np.ma.array([0.]))
    'MaskedArray([ 0.])'
    >>> np.array_repr(np.array([], np.int32))
    'array([], dtype=int32)'

    >>> x = np.array([1e-6, 4e-7, 2, 3])
    >>> np.array_repr(x, precision=6, suppress_small=True)
    'array([ 0.000001,  0.      ,  2.      ,  3.      ])'

    """
    if max_line_width is None:
        max_line_width = _format_options['linewidth']

    if type(arr) is not ndarray:
        class_name = type(arr).__name__
    else:
        class_name = "array"

    skipdtype = dtype_is_implied(arr.dtype) and arr.size > 0

    prefix = class_name + "("
    suffix = ")" if skipdtype else ","

    if (_format_options['legacy'] == '1.13' and
            arr.shape == () and not arr.dtype.names):
        lst = repr(arr.item())
    elif arr.size > 0 or arr.shape == (0,):
        lst = array2string(arr, max_line_width, precision, suppress_small,
                           ', ', prefix, suffix=suffix)
    else:  # show zero-length shape unless it is (0,)
        lst = "[], shape=%s" % (repr(arr.shape),)

    arr_str = prefix + lst + suffix

    if skipdtype:
        return arr_str

    dtype_str = "dtype={})".format(dtype_short_repr(arr.dtype))

    # compute whether we should put dtype on a new line: Do so if adding the
    # dtype would extend the last line past max_line_width.
    # Note: This line gives the correct result even when rfind returns -1.
    last_line_len = len(arr_str) - (arr_str.rfind('\n') + 1)
    spacer = " "
    if _format_options['legacy'] == '1.13':
        if issubclass(arr.dtype.type, flexible):
            spacer = '\n' + ' '*len(class_name + "(")
    elif last_line_len + len(dtype_str) + 1 > max_line_width:
        spacer = '\n' + ' '*len(class_name + "(")

    return arr_str + spacer + dtype_str