def take_fast(arr, indexer, mask, needs_masking, axis=0, out=None,
              fill_value=np.nan):
    if arr.ndim == 2:
        return take_2d(arr, indexer, out=out, mask=mask,
                       needs_masking=needs_masking,
                       axis=axis, fill_value=fill_value)

    result = arr.take(indexer, axis=axis, out=out)
    result = _maybe_mask(result, mask, needs_masking, axis=axis,
                         out_passed=out is not None, fill_value=fill_value)
    return result