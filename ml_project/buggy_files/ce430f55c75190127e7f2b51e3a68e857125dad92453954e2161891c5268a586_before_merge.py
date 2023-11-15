def ptx_atomic_cas_tuple(context, builder, sig, args):
    aryty, oldty, valty = sig.args
    ary, old, val = args
    dtype = aryty.dtype

    lary = context.make_array(aryty)(context, builder, ary)
    zero = context.get_constant(types.intp, 0)
    ptr = cgutils.get_item_pointer(builder, aryty, lary, (zero,))
    if aryty.dtype == types.int32:
        lmod = builder.module
        return builder.call(nvvmutils.declare_atomic_cas_int32(lmod),
                            (ptr, old, val))
    else:
        raise TypeError('Unimplemented atomic compare_and_swap '
                        'with %s array' % dtype)