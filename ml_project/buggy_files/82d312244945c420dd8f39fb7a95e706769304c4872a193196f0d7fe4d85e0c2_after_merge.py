def array_angle_kwarg(context, builder, sig, args):
    arg = sig.args[0]
    ret_dtype = sig.return_type.dtype

    def array_angle_impl(arr, deg):
        out = numpy.zeros_like(arr, dtype=ret_dtype)
        for index, val in numpy.ndenumerate(arr):
            out[index] = numpy.angle(val, deg)
        return out

    if len(args) == 1:
        args = args + (cgutils.false_bit,)
        sig = signature(sig.return_type, *(sig.args + (types.boolean,)))

    res = context.compile_internal(builder, array_angle_impl, sig, args)
    return impl_ret_new_ref(context, builder, sig.return_type, res)