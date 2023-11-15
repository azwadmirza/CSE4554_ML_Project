def fancy_setslice(context, builder, sig, args, index_types, indices):
    """
    Implement slice assignment for arrays.  This implementation works for
    basic as well as fancy indexing, since there's no functional difference
    between the two for indexed assignment.
    """
    aryty, _, srcty = sig.args
    ary, _, src = args

    ary = make_array(aryty)(context, builder, ary)
    dest_shapes = cgutils.unpack_tuple(builder, ary.shape)
    dest_strides = cgutils.unpack_tuple(builder, ary.strides)
    dest_data = ary.data

    indexer = FancyIndexer(context, builder, aryty, ary,
                           index_types, indices)
    indexer.prepare()

    if isinstance(srcty, types.Buffer):
        # Source is an array
        src_dtype = srcty.dtype
        index_shape = indexer.get_shape()
        src = make_array(srcty)(context, builder, src)
        # Broadcast source array to shape
        srcty, src = _broadcast_to_shape(context, builder, srcty, src,
                                         index_shape)
        src_shapes = cgutils.unpack_tuple(builder, src.shape)
        src_strides = cgutils.unpack_tuple(builder, src.strides)
        src_data = src.data

        # Check shapes are equal
        shape_error = cgutils.false_bit
        assert len(index_shape) == len(src_shapes)

        for u, v in zip(src_shapes, index_shape):
            shape_error = builder.or_(shape_error,
                                      builder.icmp_signed('!=', u, v))

        with builder.if_then(shape_error, likely=False):
            msg = "cannot assign slice from input of different size"
            context.call_conv.return_user_exc(builder, ValueError, (msg,))

        # Check for array overlap
        src_start, src_end = get_array_memory_extents(context, builder, srcty,
                                                      src, src_shapes,
                                                      src_strides, src_data)

        dest_lower, dest_upper = indexer.get_offset_bounds(dest_strides,
                                                           ary.itemsize)
        dest_start, dest_end = compute_memory_extents(context, builder,
                                                      dest_lower, dest_upper,
                                                      dest_data)

        use_copy = extents_may_overlap(context, builder, src_start, src_end,
                                       dest_start, dest_end)

        src_getitem, src_cleanup = maybe_copy_source(context, builder, use_copy,
                                                     srcty, src, src_shapes,
                                                     src_strides, src_data)

    elif isinstance(srcty, types.Sequence):
        src_dtype = srcty.dtype

        # Check shape is equal to sequence length
        index_shape = indexer.get_shape()
        assert len(index_shape) == 1
        len_impl = context.get_function(len, signature(types.intp, srcty))
        seq_len = len_impl(builder, (src,))

        shape_error = builder.icmp_signed('!=', index_shape[0], seq_len)

        with builder.if_then(shape_error, likely=False):
            msg = "cannot assign slice from input of different size"
            context.call_conv.return_user_exc(builder, ValueError, (msg,))

        def src_getitem(source_indices):
            idx, = source_indices
            getitem_impl = context.get_function(
                operator.getitem,
                signature(src_dtype, srcty, types.intp),
            )
            return getitem_impl(builder, (src, idx))

        def src_cleanup():
            pass

    else:
        # Source is a scalar (broadcast or not, depending on destination
        # shape).
        src_dtype = srcty

        def src_getitem(source_indices):
            return src

        def src_cleanup():
            pass

    # Loop on destination and copy from source to destination
    dest_indices, counts = indexer.begin_loops()

    # Source is iterated in natural order
    source_indices = tuple(c for c in counts if c is not None)
    val = src_getitem(source_indices)

    # Cast to the destination dtype (cross-dtype slice assignement is allowed)
    val = context.cast(builder, val, src_dtype, aryty.dtype)

    # No need to check for wraparound, as the indexers all ensure
    # a positive index is returned.
    dest_ptr = cgutils.get_item_pointer2(builder, dest_data,
                                         dest_shapes, dest_strides,
                                         aryty.layout, dest_indices,
                                         wraparound=False)
    store_item(context, builder, aryty, val, dest_ptr)

    indexer.end_loops()

    src_cleanup()

    return context.get_dummy_value()