def _is_potential_multi_index(columns):
    """
    Check whether or not the `columns` parameter
    could be converted into a MultiIndex.

    Parameters
    ----------
    columns : array-like
        Object which may or may not be convertible into a MultiIndex

    Returns
    -------
    boolean : Whether or not columns could become a MultiIndex
    """
    return (
        len(columns)
        and not isinstance(columns, MultiIndex)
        and all(isinstance(c, tuple) for c in columns)
    )