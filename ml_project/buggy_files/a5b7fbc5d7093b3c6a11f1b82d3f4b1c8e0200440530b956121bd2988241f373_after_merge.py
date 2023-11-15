def _interleaved_dtype(blocks):
    from collections import defaultdict
    counts = defaultdict(lambda: 0)
    for x in blocks:
        counts[type(x)] += 1

    have_int = counts[IntBlock] > 0
    have_bool = counts[BoolBlock] > 0
    have_object = counts[ObjectBlock] > 0
    have_float = counts[FloatBlock] > 0
    have_complex = counts[ComplexBlock] > 0
    have_dt64 = counts[DatetimeBlock] > 0
    have_numeric = have_float or have_complex or have_int

    if (have_object or
        (have_bool and have_numeric) or
        (have_numeric and have_dt64)):
        return np.dtype(object)
    elif have_bool:
        return np.dtype(bool)
    elif have_int and not have_float and not have_complex:
        return np.dtype('i8')
    elif have_dt64 and not have_float and not have_complex:
        return np.dtype('M8[ns]')
    elif have_complex:
        return np.dtype('c16')
    else:
        return np.dtype('f8')