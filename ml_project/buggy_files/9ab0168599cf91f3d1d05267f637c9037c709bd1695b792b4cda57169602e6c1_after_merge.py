def range_iter_len(typingctx, val):
    """
    An implementation of len(range_iter) for internal use.
    """
    if isinstance(val, types.RangeIteratorType):
        val_type = val.yield_type
        def codegen(context, builder, sig, args):
            (value,) = args
            iter_type = range_impl_map[val_type][1]
            iterobj = cgutils.create_struct_proxy(iter_type)(context, builder, value)
            int_type = iterobj.count.type
            return impl_ret_untracked(context, builder, int_type, builder.load(iterobj.count))
        return signature(val_type, val), codegen
    elif isinstance(val, types.ListIter):
        def codegen(context, builder, sig, args):
            (value,) = args
            intp_t = context.get_value_type(types.intp)
            iterobj = ListIterInstance(context, builder, sig.args[0], value)
            return impl_ret_untracked(context, builder, intp_t, iterobj.size)
        return signature(types.intp, val), codegen
    elif isinstance(val, types.ArrayIterator):
        def  codegen(context, builder, sig, args):
            (iterty,) = sig.args
            (value,) = args
            intp_t = context.get_value_type(types.intp)
            iterobj = context.make_helper(builder, iterty, value=value)
            arrayty = iterty.array_type
            ary = make_array(arrayty)(context, builder, value=iterobj.array)
            shape = cgutils.unpack_tuple(builder, ary.shape)
            # array iterates along the outer dimension
            return impl_ret_untracked(context, builder, intp_t, shape[0])
        return signature(types.intp, val), codegen