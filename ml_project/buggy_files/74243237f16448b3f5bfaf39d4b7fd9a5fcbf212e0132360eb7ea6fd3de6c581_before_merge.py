def _min_or_max_filter(input, size, ftprnt, structure, output, mode, cval,
                       origin, func):
    # structure is used by morphology.grey_erosion() and grey_dilation()
    # and not by the regular min/max filters

    sizes, ftprnt, structure = _filters_core._check_size_footprint_structure(
        input.ndim, size, ftprnt, structure)

    if sizes is not None:
        # Seperable filter, run as a series of 1D filters
        fltr = minimum_filter1d if func == 'min' else maximum_filter1d
        return _filters_core._run_1d_filters(
            [fltr if size > 1 else None for size in sizes],
            input, sizes, output, mode, cval, origin)

    origins, int_type = _filters_core._check_nd_args(input, ftprnt,
                                                     mode, origin, 'footprint')
    if structure is not None and structure.ndim != input.ndim:
        raise RuntimeError('structure array has incorrect shape')

    if ftprnt.size == 0:
        return cupy.zeros_like(input)
    offsets = _filters_core._origins_to_offsets(origins, ftprnt.shape)
    kernel = _get_min_or_max_kernel(mode, ftprnt.shape, func,
                                    offsets, float(cval), int_type,
                                    has_structure=structure is not None,
                                    has_central_value=bool(ftprnt[offsets]))
    return _filters_core._call_kernel(kernel, input, ftprnt, output,
                                      structure, weights_dtype=bool)