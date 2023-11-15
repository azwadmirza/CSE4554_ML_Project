def _exec_fftn(a, direction, value_type, norm, axes, overwrite_x,
               plan=None, out=None, out_size=None):

    fft_type = _convert_fft_type(a.dtype, value_type)

    if a.flags.c_contiguous:
        order = 'C'
    elif a.flags.f_contiguous:
        order = 'F'
    else:
        raise ValueError('a must be contiguous')

    curr_plan = cufft.get_current_plan()
    if curr_plan is not None:
        plan = curr_plan
        # don't check repeated usage; it's done in _default_fft_func()
    if plan is None:
        # generate a plan
        plan = _get_cufft_plan_nd(a.shape, fft_type, axes=axes, order=order,
                                  out_size=out_size)
    else:
        if not isinstance(plan, cufft.PlanNd):
            raise ValueError('expected plan to have type cufft.PlanNd')
        if order != plan.order:
            raise ValueError('array orders mismatch (plan: {}, input: {})'
                             .format(plan.order, order))
        if a.flags.c_contiguous:
            expected_shape = [a.shape[ax] for ax in axes]
            if value_type == 'C2R':
                expected_shape[-1] = out_size
        else:
            # plan.shape will be reversed for Fortran-ordered inputs
            expected_shape = [a.shape[ax] for ax in axes[::-1]]
            # TODO(leofang): modify the shape for C2R
        expected_shape = tuple(expected_shape)
        if expected_shape != plan.shape:
            raise ValueError(
                'The cuFFT plan and a.shape do not match: '
                'plan.shape = {}, expected_shape={}, a.shape = {}'.format(
                    plan.shape, expected_shape, a.shape))
        if fft_type != plan.fft_type:
            raise ValueError('cuFFT plan dtype mismatch.')
        if value_type != 'C2C':
            if axes[-1] != plan.last_axis:
                raise ValueError('The last axis for R2C/C2R mismatch')
            if out_size != plan.last_size:
                raise ValueError('The size along the last R2C/C2R axis '
                                 'mismatch')

    # TODO(leofang): support in-place transform for R2C/C2R
    if overwrite_x and value_type == 'C2C':
        out = a
    elif out is None:
        out = plan.get_output_array(a, order=order)
    else:
        plan.check_output_array(a, out)

    if out.size != 0:
        plan.fft(a, out, direction)

    # normalize by the product of the shape along the transformed axes
    arr = a if fft_type in (cufft.CUFFT_R2C, cufft.CUFFT_D2Z) else out
    sz = _prod([arr.shape[ax] for ax in axes])
    if norm is None:
        if direction == cufft.CUFFT_INVERSE:
            out /= sz
    else:
        out /= math.sqrt(sz)

    return out