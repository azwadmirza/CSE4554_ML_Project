    def codegen(context, builder, sig, args):
        ll_unified_ty = context.get_data_type(unified_ty)
        idx = builder.sext(args[0], ll_unified_ty)
        size = builder.sext(args[1], ll_unified_ty)
        neg_size = builder.neg(size)
        zero = llvmlite.ir.Constant(ll_unified_ty, 0)
        idx_negative = builder.icmp_signed('<', idx, zero)
        pos_oversize = builder.icmp_signed('>=', idx, size)
        neg_oversize = builder.icmp_signed('<=', idx, neg_size)
        pos_res = builder.select(pos_oversize, size, idx)
        neg_res = builder.select(neg_oversize, zero, builder.add(idx, size))
        mod = builder.select(idx_negative, neg_res, pos_res)
        return mod