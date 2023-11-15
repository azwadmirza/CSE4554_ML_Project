def hsail_atomic_add_tuple(context, builder, sig, args):
    aryty, indty, valty = sig.args
    ary, inds, val = args
    dtype = aryty.dtype

    if indty == types.intp:
        indices = [inds]  # just a single integer
        indty = [indty]
    else:
        indices = cgutils.unpack_tuple(builder, inds, count=len(indty))
        indices = [context.cast(builder, i, t, types.intp)
                   for t, i in zip(indty, indices)]

    if dtype != valty:
        raise TypeError("expecting %s but got %s" % (dtype, valty))

    if aryty.ndim != len(indty):
        raise TypeError("indexing %d-D array with %d-D index" %
                        (aryty.ndim, len(indty)))

    lary = context.make_array(aryty)(context, builder, ary)
    ptr = cgutils.get_item_pointer(context, builder, aryty, lary, indices)

    return builder.atomic_rmw("add", ptr, val, ordering='monotonic')