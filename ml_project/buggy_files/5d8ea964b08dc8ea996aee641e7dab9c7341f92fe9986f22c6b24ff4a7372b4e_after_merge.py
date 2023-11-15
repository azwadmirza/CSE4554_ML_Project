def memset(builder, ptr, size, value):
    """
    Fill *size* bytes starting from *ptr* with *value*.
    """
    fn = builder.module.declare_intrinsic('llvm.memset', (voidptr_t, size.type))
    ptr = builder.bitcast(ptr, voidptr_t)
    if isinstance(value, int):
        value = int8_t(value)
    builder.call(fn, [ptr, value, size, bool_t(0)])