def _get_zoom_kernel(ndim, large_int, yshape, mode, cval=0.0, order=1,
                     integer_output=False):
    in_params = 'raw X x, raw W zoom'
    out_params = 'Y y'
    operation, name = _generate_interp_custom(
        coord_func=_get_coord_zoom,
        ndim=ndim,
        large_int=large_int,
        yshape=yshape,
        mode=mode,
        cval=cval,
        order=order,
        name='zoom',
        integer_output=integer_output,
    )
    return cupy.ElementwiseKernel(in_params, out_params, operation, name,
                                  preamble=math_constants_preamble)