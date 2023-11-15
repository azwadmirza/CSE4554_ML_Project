def _do_concatenate(context, builder, axis,
                    arrtys, arrs, arr_shapes, arr_strides,
                    retty, ret_shapes):
    """
    Concatenate arrays along the given axis.
    """
    assert len(arrtys) == len(arrs) == len(arr_shapes) == len(arr_strides)

    zero = cgutils.intp_t(0)

    # Allocate return array
    ret = _empty_nd_impl(context, builder, retty, ret_shapes)
    ret_strides = cgutils.unpack_tuple(builder, ret.strides)

    # Compute the offset by which to bump the destination pointer
    # after copying each input array.
    # Morally, we need to copy each input array at different start indices
    # into the destination array; bumping the destination pointer
    # is simply easier than offsetting all destination indices.
    copy_offsets = []

    for arr_sh in arr_shapes:
        # offset = ret_strides[axis] * input_shape[axis]
        offset = zero
        for dim, (size, stride) in enumerate(zip(arr_sh, ret_strides)):
            is_axis = builder.icmp_signed('==', axis.type(dim), axis)
            addend = builder.mul(size, stride)
            offset = builder.select(is_axis,
                                    builder.add(offset, addend),
                                    offset)
        copy_offsets.append(offset)

    # Copy input arrays into the return array
    ret_data = ret.data

    for arrty, arr, arr_sh, arr_st, offset in zip(arrtys, arrs, arr_shapes,
                                                  arr_strides, copy_offsets):
        arr_data = arr.data

        # Do the copy loop
        # Note the loop nesting is optimized for the destination layout
        loop_nest = cgutils.loop_nest(builder, arr_sh, cgutils.intp_t,
                                      order=retty.layout)

        with loop_nest as indices:
            src_ptr = cgutils.get_item_pointer2(builder, arr_data,
                                                arr_sh, arr_st,
                                                arrty.layout, indices)
            val = load_item(context, builder, arrty, src_ptr)
            val = context.cast(builder, val, arrty.dtype, retty.dtype)
            dest_ptr = cgutils.get_item_pointer2(builder, ret_data,
                                                 ret_shapes, ret_strides,
                                                 retty.layout, indices)
            store_item(context, builder, retty, val, dest_ptr)

        # Bump destination pointer
        ret_data = cgutils.pointer_add(builder, ret_data, offset)

    return ret