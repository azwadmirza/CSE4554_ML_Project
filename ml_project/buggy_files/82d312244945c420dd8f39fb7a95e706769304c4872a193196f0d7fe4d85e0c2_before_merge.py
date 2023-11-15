def array_angle_kwarg(context, builder, sig, args):
    arg = sig.args[0]
    if isinstance(arg.dtype, types.Complex):
        retty = arg.dtype.underlying_float
    else:
        retty = arg.dtype
    def array_angle_impl(arr, deg=False):
        out = numpy.zeros_like(arr, dtype=retty)
        for index, val in numpy.ndenumerate(arr):
            out[index] = numpy.angle(val, deg)
        return out
    res = context.compile_internal(builder, array_angle_impl, sig, args)
    return impl_ret_new_ref(context, builder, sig.return_type, res)