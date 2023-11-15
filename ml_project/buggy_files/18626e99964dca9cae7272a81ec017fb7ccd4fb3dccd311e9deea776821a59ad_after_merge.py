def scalar_angle_kwarg(context, builder, sig, args):
    deg_mult = sig.return_type(180 / numpy.pi)
    def scalar_angle_impl(val, deg):
        if deg:
            return numpy.arctan2(val.imag, val.real) * deg_mult
        else:
            return numpy.arctan2(val.imag, val.real)

    if len(args) == 1:
        args = args + (cgutils.false_bit,)
        sig = signature(sig.return_type, *(sig.args + (types.boolean,)))
    res = context.compile_internal(builder, scalar_angle_impl,
                                   sig, args)
    return impl_ret_untracked(context, builder, sig.return_type, res)