def wrap_index(typingctx, idx, size):
    """
    Calculate index value "idx" relative to a size "size" value as
    (idx % size), where "size" is known to be positive.
    Note that we use the mod(%) operation here instead of
    (idx < 0 ? idx + size : idx) because we may have situations
    where idx > size due to the way indices are calculated
    during slice/range analysis.
    """
    if idx != size:
        raise ValueError("Argument types for wrap_index must match")

    def codegen(context, builder, sig, args):
        assert(len(args) == 2)
        idx = args[0]
        size = args[1]
        rem = builder.srem(idx, size)
        zero = llvmlite.ir.Constant(idx.type, 0)
        is_negative = builder.icmp_signed('<', rem, zero)
        wrapped_rem = builder.add(rem, size)
        is_oversize = builder.icmp_signed('>', wrapped_rem, size)
        mod = builder.select(is_negative, wrapped_rem,
                builder.select(is_oversize, rem, wrapped_rem))
        return mod

    return signature(idx, idx, size), codegen