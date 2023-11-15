def wrap_index(typingctx, idx, size):
    """
    Calculate index value "idx" relative to a size "size" value as
    (idx % size), where "size" is known to be positive.
    Note that we use the mod(%) operation here instead of
    (idx < 0 ? idx + size : idx) because we may have situations
    where idx > size due to the way indices are calculated
    during slice/range analysis.
    """
    unified_ty = typingctx.unify_types(idx, size)
    # Mixing signed and unsigned ints will unify to double which is
    # no good for indexing.  If the unified type is not an integer
    # then just use int64 as the common index type.  This does have
    # some overflow potential if the unsigned value is greater than
    # 2**63.
    if not isinstance(unified_ty, types.Integer):
        unified_ty = types.int64

    def codegen(context, builder, sig, args):
        ll_unified_ty = context.get_data_type(unified_ty)
        idx = builder.sext(args[0], ll_unified_ty)
        size = builder.sext(args[1], ll_unified_ty)
        neg_size = builder.neg(size)
        zero = llvmlite.ir.Constant(ll_unified_ty, 0)
        idx_negative = builder.icmp_signed("<", idx, zero)
        pos_oversize = builder.icmp_signed(">=", idx, size)
        neg_oversize = builder.icmp_signed("<=", idx, neg_size)
        pos_res = builder.select(pos_oversize, size, idx)
        neg_res = builder.select(neg_oversize, zero, builder.add(idx, size))
        mod = builder.select(idx_negative, neg_res, pos_res)
        return mod

    return signature(unified_ty, idx, size), codegen