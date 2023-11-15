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