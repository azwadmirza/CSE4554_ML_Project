def _raw_memcpy(builder, func_name, dst, src, count, itemsize, align):
    size_t = count.type
    if isinstance(itemsize, utils.INT_TYPES):
        itemsize = ir.Constant(size_t, itemsize)

    memcpy = builder.module.declare_intrinsic(func_name,
                                              [voidptr_t, voidptr_t, size_t])
    is_volatile = false_bit
    builder.call(memcpy, [builder.bitcast(dst, voidptr_t),
                          builder.bitcast(src, voidptr_t),
                          builder.mul(count, itemsize),
                          is_volatile])