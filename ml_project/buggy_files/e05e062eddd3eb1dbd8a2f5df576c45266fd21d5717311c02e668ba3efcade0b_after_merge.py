def _fft(a, s, axes, norm, direction, value_type='C2C', overwrite_x=False,
         plan=None):
    if norm not in (None, 'ortho'):
        raise ValueError('Invalid norm value %s, should be None or "ortho".'
                         % norm)

    if (s is not None) and (axes is not None) and len(s) != len(axes):
        raise ValueError('Shape and axes have different lengths.')

    if axes is None:
        if s is None:
            dim = a.ndim
        else:
            dim = len(s)
        axes = [i for i in range(-dim, 0)]
    else:
        axes = tuple(axes)
    if not axes:
        if value_type == 'C2C':
            return a
        else:
            raise IndexError('list index out of range')
    a = _convert_dtype(a, value_type)
    a = _cook_shape(a, s, axes, value_type)

    if value_type == 'C2C':
        a = _fft_c2c(a, direction, norm, axes, overwrite_x, plan=plan)
    elif value_type == 'R2C':
        a = _exec_fft(a, direction, value_type, norm, axes[-1], overwrite_x)
        a = _fft_c2c(a, direction, norm, axes[:-1], overwrite_x)
    else:  # C2R
        a = _fft_c2c(a, direction, norm, axes[:-1], overwrite_x)
        # _cook_shape tells us input shape only, and no output shape
        out_size = _get_fftn_out_size(a.shape, s, axes[-1], value_type)
        a = _exec_fft(a, direction, value_type, norm, axes[-1], overwrite_x,
                      out_size)

    return a