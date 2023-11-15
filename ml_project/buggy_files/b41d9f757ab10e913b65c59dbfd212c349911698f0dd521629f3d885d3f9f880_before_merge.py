def take_2d(arr, indexer, out=None, mask=None, needs_masking=None, axis=0,
            fill_value=np.nan):
    """
    Specialized Cython take which sets NaN values in one pass
    """
    dtype_str = arr.dtype.name

    out_shape = list(arr.shape)
    out_shape[axis] = len(indexer)
    out_shape = tuple(out_shape)

    if not isinstance(indexer, np.ndarray):
        # Cython methods expects 32-bit integers
        indexer = np.array(indexer, dtype=np.int32)

    if dtype_str in ('int32', 'int64', 'bool'):
        if mask is None:
            mask = indexer == -1
            needs_masking = mask.any()

        if needs_masking:
            # upcasting may be required
            result = arr.take(indexer, axis=axis, out=out)
            result = _maybe_mask(result, mask, needs_masking, axis=axis,
                                 out_passed=out is not None,
                                 fill_value=fill_value)
            return result
        else:
            if out is None:
                out = np.empty(out_shape, dtype=arr.dtype)
            take_f = _get_take2d_function(dtype_str, axis=axis)
            take_f(arr, indexer, out=out, fill_value=fill_value)
            return out
    elif dtype_str in ('float64', 'object'):
        if out is None:
            out = np.empty(out_shape, dtype=arr.dtype)
        take_f = _get_take2d_function(dtype_str, axis=axis)
        take_f(arr, indexer, out=out, fill_value=fill_value)
        return out
    else:
        if mask is None:
            mask = indexer == -1
            needs_masking = mask.any()

        # GH #486
        if out is not None and arr.dtype != out.dtype:
            arr = arr.astype(out.dtype)

        result = arr.take(indexer, axis=axis, out=out)
        result = _maybe_mask(result, mask, needs_masking, axis=axis,
                             out_passed=out is not None,
                             fill_value=fill_value)
        return result