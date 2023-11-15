def _interleaved_dtype(blocks):
    from collections import defaultdict
    counts = defaultdict(lambda: 0)
    for x in blocks:
        counts[type(x)] += 1

    have_int = counts[IntBlock] > 0
    have_bool = counts[BoolBlock] > 0
    have_object = counts[ObjectBlock] > 0
    have_float = counts[FloatBlock] > 0
    have_numeric = have_float or have_int

    if have_object:
        return np.object_
    elif have_bool and have_numeric:
        return np.object_
    elif have_bool:
        return np.bool_
    elif have_int and not have_float:
        return np.int64
    else:
        return np.float64