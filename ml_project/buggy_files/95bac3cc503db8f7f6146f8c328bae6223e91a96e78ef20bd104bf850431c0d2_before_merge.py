def _ensure_datetimelike_to_i8(other):
    """ helper for coercing an input scalar or array to i8 """
    if is_scalar(other) and isna(other):
        other = iNaT
    elif isinstance(other, ABCIndexClass):
        # convert tz if needed
        if getattr(other, 'tz', None) is not None:
            other = other.tz_localize(None).asi8
        else:
            other = other.asi8
    else:
        try:
            other = np.array(other, copy=False).view('i8')
        except TypeError:
            # period array cannot be coerces to int
            other = Index(other).asi8
    return other