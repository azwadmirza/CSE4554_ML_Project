def take_1d(arr, indexer, out=None, fill_value=np.nan):
    """
    Specialized Cython take which sets NaN values in one pass
    """
    dtype_str = arr.dtype.name

    n = len(indexer)

    if not isinstance(indexer, np.ndarray):
        # Cython methods expects 32-bit integers
        indexer = np.array(indexer, dtype=np.int32)

    out_passed = out is not None

    if dtype_str in ('int32', 'int64', 'bool'):
        try:
            if out is None:
                out = np.empty(n, dtype=arr.dtype)
            take_f = _take1d_dict[dtype_str]
            take_f(arr, indexer, out=out, fill_value=fill_value)
        except ValueError:
            mask = indexer == -1
            if len(arr) == 0:
                if not out_passed:
                    out = np.empty(n, dtype=arr.dtype)
            else:
                out = arr.take(indexer, out=out)
            if mask.any():
                if out_passed:
                    raise Exception('out with dtype %s does not support NA' %
                                    out.dtype)
                out = _maybe_upcast(out)
                np.putmask(out, mask, fill_value)
    elif dtype_str in ('float64', 'object'):
        if out is None:
            out = np.empty(n, dtype=arr.dtype)
        take_f = _take1d_dict[dtype_str]
        take_f(arr, indexer, out=out, fill_value=fill_value)
    else:
        out = arr.take(indexer, out=out)
        mask = indexer == -1
        if mask.any():
            if out_passed:
                raise Exception('out with dtype %s does not support NA' %
                                out.dtype)
            out = _maybe_upcast(out)
            np.putmask(out, mask, fill_value)

    return out