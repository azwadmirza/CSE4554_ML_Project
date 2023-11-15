    def imp(context, builder, sig, args):
        # The common argument handling code
        aryty, indty, valty = sig.args
        ary, inds, val = args
        dtype = aryty.dtype

        indty, indices = _normalize_indices(context, builder, indty, inds)

        if dtype != valty:
            raise TypeError("expect %s but got %s" % (dtype, valty))

        if aryty.ndim != len(indty):
            raise TypeError("indexing %d-D array with %d-D index" %
                            (aryty.ndim, len(indty)))

        lary = context.make_array(aryty)(context, builder, ary)
        ptr = cgutils.get_item_pointer(context, builder, aryty, lary, indices)
        # dispatcher to implementation base on dtype
        return dispatch_fn(context, builder, dtype, ptr, val)