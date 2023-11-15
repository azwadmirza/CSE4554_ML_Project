def _ensure_datetimelike_to_i8(other, to_utc=False):
    """
    Helper for coercing an input scalar or array to i8.

    Parameters
    ----------
    other : 1d array
    to_utc : bool, default False
        If True, convert the values to UTC before extracting the i8 values
        If False, extract the i8 values directly.

    Returns
    -------
    i8 1d array
    """
    from pandas import Index
    from pandas.core.arrays import PeriodArray

    if lib.is_scalar(other) and isna(other):
        return iNaT
    elif isinstance(other, (PeriodArray, ABCIndexClass)):
        # convert tz if needed
        if getattr(other, 'tz', None) is not None:
            if to_utc:
                other = other.tz_convert('UTC')
            else:
                other = other.tz_localize(None)
    else:
        try:
            return np.array(other, copy=False).view('i8')
        except TypeError:
            # period array cannot be coerced to int
            other = Index(other)
    return other.asi8