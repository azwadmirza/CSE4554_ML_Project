def take_2d_multi(arr, row_idx, col_idx, fill_value=np.nan):

    dtype_str = arr.dtype.name

    out_shape = len(row_idx), len(col_idx)

    if dtype_str in ('int32', 'int64', 'bool'):
        row_mask = row_idx == -1
        col_mask=  col_idx == -1
        needs_masking = row_mask.any() or col_mask.any()

        if needs_masking:
            return take_2d_multi(_maybe_upcast(arr), row_idx, col_idx,
                                 fill_value=fill_value)
        else:
            out = np.empty(out_shape, dtype=arr.dtype)
            take_f = _get_take2d_function(dtype_str, axis='multi')
            take_f(arr, _ensure_int64(row_idx),
                   _ensure_int64(col_idx), out=out,
                   fill_value=fill_value)
            return out
    elif dtype_str in ('float64', 'object', 'datetime64[ns]'):
        out = np.empty(out_shape, dtype=arr.dtype)
        take_f = _get_take2d_function(dtype_str, axis='multi')
        take_f(arr, _ensure_int64(row_idx), _ensure_int64(col_idx), out=out,
               fill_value=fill_value)
        return out
    else:
        return take_2d(take_2d(arr, row_idx, axis=0, fill_value=fill_value),
                       col_idx, axis=1, fill_value=fill_value)