def _exec_fft(a, direction, value_type, norm, axis, overwrite_x,
              out_size=None, out=None, plan=None):
    fft_type = _convert_fft_type(a.dtype, value_type)

    if axis % a.ndim != a.ndim - 1:
        a = a.swapaxes(axis, -1)

    if a.base is not None or not a.flags.c_contiguous:
        a = a.copy()

    if out_size is None:
        out_size = a.shape[-1]

    batch = a.size // a.shape[-1]
    curr_plan = cufft.get_current_plan()
    if curr_plan is not None:
        if plan is None:
            plan = curr_plan
        else:
            raise RuntimeError('Use the cuFFT plan either as a context manager'
                               ' or as an argument.')
    if plan is None:
        devices = None if not config.use_multi_gpus else config._devices
        plan = cufft.Plan1d(out_size, fft_type, batch, devices=devices)
    else:
        # check plan validity
        if not isinstance(plan, cufft.Plan1d):
            raise ValueError('expected plan to have type cufft.Plan1d')
        if fft_type != plan.fft_type:
            raise ValueError('cuFFT plan dtype mismatch.')
        if out_size != plan.nx:
            raise ValueError('Target array size does not match the plan.',
                             out_size, plan.nx)
        if batch != plan.batch:
            raise ValueError('Batch size does not match the plan.')
        if config.use_multi_gpus != plan._use_multi_gpus:
            raise ValueError('Unclear if multiple GPUs are to be used or not.')

    if overwrite_x and value_type == 'C2C':
        out = a
    elif out is not None:
        # verify that out has the expected shape and dtype
        plan.check_output_array(a, out)
    else:
        out = plan.get_output_array(a)

    plan.fft(a, out, direction)

    sz = out.shape[-1]
    if fft_type == cufft.CUFFT_R2C or fft_type == cufft.CUFFT_D2Z:
        sz = a.shape[-1]
    if norm is None:
        if direction == cufft.CUFFT_INVERSE:
            out /= sz
    else:
        out /= math.sqrt(sz)

    if axis % a.ndim != a.ndim - 1:
        out = out.swapaxes(axis, -1)

    return out