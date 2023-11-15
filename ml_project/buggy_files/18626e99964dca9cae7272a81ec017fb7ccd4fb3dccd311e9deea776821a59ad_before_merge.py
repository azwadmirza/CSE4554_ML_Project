def scalar_angle_kwarg(context, builder, sig, args):
    def scalar_angle_impl(val, deg=False):
        if deg:
            scal = 180/numpy.pi
            return numpy.arctan2(val.imag, val.real) * scal
        else:
            return numpy.arctan2(val.imag, val.real)
    res = context.compile_internal(builder, scalar_angle_impl,
                                      sig, args)
    return impl_ret_untracked(context, builder, sig.return_type, res)