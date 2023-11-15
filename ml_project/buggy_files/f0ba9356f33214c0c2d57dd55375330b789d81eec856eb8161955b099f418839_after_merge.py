def take_1d(arr, indexer, out=None, fill_value=np.nan):
    """
    Specialized Cython take which sets NaN values in one pass
    """
    dtype_str = arr.dtype.name

    n = len(indexer)

    indexer = _ensure_int64(indexer)

    out_passed = out is not None
    take_f = _take1d_dict.get(dtype_str)

    if dtype_str in ('int32', 'int64', 'bool'):
        try:
            if out is None:
                out = np.empty(n, dtype=arr.dtype)
            take_f(arr, _ensure_int64(indexer), out=out, fill_value=fill_value)
        except ValueError:
            mask = indexer == -1
            if len(arr) == 0:
                if not out_passed:
                    out = np.empty(n, dtype=arr.dtype)
            else:
                out = ndtake(arr, indexer, out=out)
            if mask.any():
                if out_passed:
                    raise Exception('out with dtype %s does not support NA' %
                                    out.dtype)
                out = _maybe_upcast(out)
                np.putmask(out, mask, fill_value)
    elif dtype_str in ('float64', 'object', 'datetime64[ns]'):
        if out is None:
            out = np.empty(n, dtype=arr.dtype)
        take_f(arr, _ensure_int64(indexer), out=out, fill_value=fill_value)
    else:
        out = ndtake(arr, indexer, out=out)
        mask = indexer == -1
        if mask.any():
            if out_passed:
                raise Exception('out with dtype %s does not support NA' %
                                out.dtype)
            out = _maybe_upcast(out)
            np.putmask(out, mask, fill_value)

    return out