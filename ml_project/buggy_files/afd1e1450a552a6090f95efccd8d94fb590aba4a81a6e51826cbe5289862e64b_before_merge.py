def default_fill_value(obj):
    """
    Return the default fill value for the argument object.

    The default filling value depends on the datatype of the input
    array or the type of the input scalar:

       ========  ========
       datatype  default
       ========  ========
       bool      True
       int       999999
       float     1.e20
       complex   1.e20+0j
       object    '?'
       string    'N/A'
       ========  ========


    Parameters
    ----------
    obj : ndarray, dtype or scalar
        The array data-type or scalar for which the default fill value
        is returned.

    Returns
    -------
    fill_value : scalar
        The default fill value.

    Examples
    --------
    >>> np.ma.default_fill_value(1)
    999999
    >>> np.ma.default_fill_value(np.array([1.1, 2., np.pi]))
    1e+20
    >>> np.ma.default_fill_value(np.dtype(complex))
    (1e+20+0j)

    """
    if hasattr(obj, 'dtype'):
        defval = _check_fill_value(None, obj.dtype)
    elif isinstance(obj, np.dtype):
        if obj.subdtype:
            defval = default_filler.get(obj.subdtype[0].kind, '?')
        elif obj.kind in 'Mm':
            defval = default_filler.get(obj.str[1:], '?')
        else:
            defval = default_filler.get(obj.kind, '?')
    elif isinstance(obj, float):
        defval = default_filler['f']
    elif isinstance(obj, int) or isinstance(obj, long):
        defval = default_filler['i']
    elif isinstance(obj, bytes):
        defval = default_filler['S']
    elif isinstance(obj, unicode):
        defval = default_filler['U']
    elif isinstance(obj, complex):
        defval = default_filler['c']
    else:
        defval = default_filler['O']
    return defval