def array_str(a, max_line_width=None, precision=None, suppress_small=None):
    """
    Return a string representation of the data in an array.

    The data in the array is returned as a single string.  This function is
    similar to `array_repr`, the difference being that `array_repr` also
    returns information on the kind of array and its data type.

    Parameters
    ----------
    a : ndarray
        Input array.
    max_line_width : int, optional
        Inserts newlines if text is longer than `max_line_width`.  The
        default is, indirectly, 75.
    precision : int, optional
        Floating point precision.  Default is the current printing precision
        (usually 8), which can be altered using `set_printoptions`.
    suppress_small : bool, optional
        Represent numbers "very close" to zero as zero; default is False.
        Very close is defined by precision: if the precision is 8, e.g.,
        numbers smaller (in absolute value) than 5e-9 are represented as
        zero.

    See Also
    --------
    array2string, array_repr, set_printoptions

    Examples
    --------
    >>> np.array_str(np.arange(3))
    '[0 1 2]'

    """
    if (_format_options['legacy'] == '1.13' and
            a.shape == () and not a.dtype.names):
        return str(a.item())

    # the str of 0d arrays is a special case: It should appear like a scalar,
    # so floats are not truncated by `precision`, and strings are not wrapped
    # in quotes. So we return the str of the scalar value.
    if a.shape == ():
        # obtain a scalar and call str on it, avoiding problems for subclasses
        # for which indexing with () returns a 0d instead of a scalar by using
        # ndarray's getindex. Also guard against recursive 0d object arrays.
        return _guarded_str(np.ndarray.__getitem__(a, ()))

    return array2string(a, max_line_width, precision, suppress_small, ' ', "")