def get_item_pointer2(context, builder, data, shape, strides, layout, inds,
                      wraparound=False, boundscheck=False):
    # Set boundscheck=True for any pointer access that should be
    # boundschecked. do_boundscheck() will handle enabling or disabling the
    # actual boundschecking based on the user config.
    if wraparound:
        # Wraparound
        indices = []
        for ind, dimlen in zip(inds, shape):
            negative = builder.icmp_signed('<', ind, ind.type(0))
            wrapped = builder.add(dimlen, ind)
            selected = builder.select(negative, wrapped, ind)
            indices.append(selected)
    else:
        indices = inds
    if boundscheck:
        for axis, (ind, dimlen) in enumerate(zip(indices, shape)):
            do_boundscheck(context, builder, ind, dimlen, axis)

    if not indices:
        # Indexing with empty tuple
        return builder.gep(data, [int32_t(0)])
    intp = indices[0].type
    # Indexing code
    if layout in 'CF':
        steps = []
        # Compute steps for each dimension
        if layout == 'C':
            # C contiguous
            for i in range(len(shape)):
                last = intp(1)
                for j in shape[i + 1:]:
                    last = builder.mul(last, j)
                steps.append(last)
        elif layout == 'F':
            # F contiguous
            for i in range(len(shape)):
                last = intp(1)
                for j in shape[:i]:
                    last = builder.mul(last, j)
                steps.append(last)
        else:
            raise Exception("unreachable")

        # Compute index
        loc = intp(0)
        for i, s in zip(indices, steps):
            tmp = builder.mul(i, s)
            loc = builder.add(loc, tmp)
        ptr = builder.gep(data, [loc])
        return ptr
    else:
        # Any layout
        dimoffs = [builder.mul(s, i) for s, i in zip(strides, indices)]
        offset = functools.reduce(builder.add, dimoffs)
        return pointer_add(builder, data, offset)