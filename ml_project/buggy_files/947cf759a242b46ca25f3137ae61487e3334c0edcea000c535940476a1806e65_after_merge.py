def _get_cufft_plan_nd(shape, fft_type, axes=None, order='C', out_size=None):
    """Generate a CUDA FFT plan for transforming up to three axes.

    Args:
        shape (tuple of int): The shape of the array to transform
        fft_type (int): The FFT type to perform. Supported values are:
            `cufft.CUFFT_C2C`, `cufft.CUFFT_C2R`, `cufft.CUFFT_R2C`,
            `cufft.CUFFT_Z2Z`, `cufft.CUFFT_Z2D`, and `cufft.CUFFT_D2Z`.
        axes (None or int or tuple of int):  The axes of the array to
            transform. Currently, these must be a set of up to three adjacent
            axes and must include either the first or the last axis of the
            array.  If `None`, it is assumed that all axes are transformed.
        order ({'C', 'F'}): Specify whether the data to be transformed has C or
            Fortran ordered data layout.
        out_size (int): The output length along the last axis for R2C/C2R FFTs.
            For C2C FFT, this is ignored (and set to `None`).

    Returns:
        plan (cufft.PlanNd): A cuFFT Plan for the chosen `fft_type`.
    """
    ndim = len(shape)

    if fft_type in (cufft.CUFFT_C2C, cufft.CUFFT_Z2Z):
        value_type = 'C2C'
    elif fft_type in (cufft.CUFFT_C2R, cufft.CUFFT_Z2D):
        value_type = 'C2R'
    else:  # CUFFT_R2C or CUFFT_D2Z
        value_type = 'R2C'

    if axes is None:
        # transform over all axes
        fft_axes = tuple(range(ndim))
    else:
        _, fft_axes = _prep_fftn_axes(ndim, s=None, axes=axes,
                                      value_type=value_type)

    if not _nd_plan_is_possible(fft_axes, ndim):
        raise ValueError(
            "An n-dimensional cuFFT plan could not be created. The axes must "
            "be contiguous and non-repeating. Between one and three axes can "
            "be transformed and either the first or last axis must be "
            "included in axes.")

    if order not in ['C', 'F']:
        raise ValueError('order must be \'C\' or \'F\'')

    """
    For full details on idist, istride, iembed, etc. see:
    http://docs.nvidia.com/cuda/cufft/index.html#advanced-data-layout

    in 1D:
    input[b * idist + x * istride]
    output[b * odist + x * ostride]

    in 2D:
    input[b * idist + (x * inembed[1] + y) * istride]
    output[b * odist + (x * onembed[1] + y) * ostride]

    in 3D:
    input[b * idist + ((x * inembed[1] + y) * inembed[2] + z) * istride]
    output[b * odist + ((x * onembed[1] + y) * onembed[2] + z) * ostride]
    """
    # At this point, _default_fft_func() guarantees that for F-order arrays
    # we only need to consider C2C, and not C2R or R2C.
    # TODO(leofang): figure out if we really have to skip F-order?
    in_dimensions = [shape[d] for d in fft_axes]
    if order == 'F':
        in_dimensions = in_dimensions[::-1]
    in_dimensions = tuple(in_dimensions)
    if fft_type in (cufft.CUFFT_C2C, cufft.CUFFT_Z2Z):
        out_dimensions = in_dimensions
        plan_dimensions = in_dimensions
    else:
        out_dimensions = list(in_dimensions)
        if out_size is not None:  # for C2R & R2C
            out_dimensions[-1] = out_size  # only valid for C order!
        out_dimensions = tuple(out_dimensions)
        if fft_type in (cufft.CUFFT_R2C, cufft.CUFFT_D2Z):
            plan_dimensions = in_dimensions
        else:  # CUFFT_C2R or CUFFT_Z2D
            plan_dimensions = out_dimensions
    inembed = in_dimensions
    onembed = out_dimensions

    if fft_axes == tuple(range(ndim)):
        # tranfsorm over all axes
        nbatch = 1
        idist = odist = 1  # doesn't matter since nbatch = 1
        istride = ostride = 1
    else:
        # batch along the first or the last axis
        if 0 not in fft_axes:
            # don't FFT along the first min_axis_fft axes
            min_axis_fft = _reduce(min, fft_axes)
            nbatch = _prod(shape[:min_axis_fft])
            if order == 'C':
                # C-ordered GPU array with batch along first dim
                idist = _prod(in_dimensions)
                odist = _prod(out_dimensions)
                istride = 1
                ostride = 1
            elif order == 'F':
                # F-ordered GPU array with batch along first dim
                idist = 1
                odist = 1
                istride = nbatch
                ostride = nbatch
        elif (ndim - 1) not in fft_axes:
            # don't FFT along the last axis
            num_axes_batch = ndim - len(fft_axes)
            nbatch = _prod(shape[-num_axes_batch:])
            if order == 'C':
                # C-ordered GPU array with batch along last dim
                idist = 1
                odist = 1
                istride = nbatch
                ostride = nbatch
            elif order == 'F':
                # F-ordered GPU array with batch along last dim
                idist = _prod(in_dimensions)
                odist = _prod(out_dimensions)
                istride = 1
                ostride = 1
        else:
            raise ValueError(
                'General subsets of FFT axes not currently supported for '
                'GPU case (Can only batch FFT over the first or last '
                'spatial axes).')

    for n in plan_dimensions:
        if n < 1:
            raise ValueError(
                'Invalid number of FFT data points specified.')

    plan = cufft.PlanNd(shape=plan_dimensions,
                        inembed=inembed,
                        istride=istride,
                        idist=idist,
                        onembed=onembed,
                        ostride=ostride,
                        odist=odist,
                        fft_type=fft_type,
                        batch=nbatch,
                        order=order,
                        last_axis=fft_axes[-1],
                        last_size=out_size)
    return plan