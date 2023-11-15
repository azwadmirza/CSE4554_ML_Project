def range_iter_len(typingctx, val):
    """
    An implementation of len(range_iter) for internal use.
    """
    if isinstance(val, types.RangeIteratorType):
        val_type = val.yield_type
        def codegen(context, builder, sig, args):
            (value,) = args
            iter_type = range_impl_map[val_type][1]
            state = cgutils.create_struct_proxy(iter_type)(context, builder, value)
            int_type = state.count.type
            return impl_ret_untracked(context, builder, int_type, builder.load(state.count))
        return signature(val_type, val), codegen