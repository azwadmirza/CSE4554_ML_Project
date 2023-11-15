def _rank_filter(input, get_rank, size=None, footprint=None, output=None,
                 mode="reflect", cval=0.0, origin=0):
    _, footprint, _ = _filters_core._check_size_footprint_structure(
        input.ndim, size, footprint, None, force_footprint=True)
    if cval is cupy.nan:
        raise NotImplementedError("NaN cval is unsupported")
    origins, int_type = _filters_core._check_nd_args(input, footprint,
                                                     mode, origin, 'footprint')
    if footprint.size == 0:
        return cupy.zeros_like(input)
    filter_size = int(footprint.sum())
    rank = get_rank(filter_size)
    if rank < 0 or rank >= filter_size:
        raise RuntimeError('rank not within filter footprint size')
    if rank == 0:
        return _min_or_max_filter(input, None, footprint, None, output, mode,
                                  cval, origins, 'min')
    if rank == filter_size - 1:
        return _min_or_max_filter(input, None, footprint, None, output, mode,
                                  cval, origins, 'max')
    offsets = _filters_core._origins_to_offsets(origins, footprint.shape)
    kernel = _get_rank_kernel(filter_size, rank, mode, footprint.shape,
                              offsets, float(cval), int_type)
    return _filters_core._call_kernel(kernel, input, footprint, output,
                                      weights_dtype=bool)