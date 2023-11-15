def maybe_copy_source(context, builder, use_copy,
                      srcty, src, src_shapes, src_strides, src_data):
    ptrty = src_data.type

    copy_layout = 'C'
    copy_data = cgutils.alloca_once_value(builder, src_data)
    copy_shapes = src_shapes
    copy_strides = None  # unneeded for contiguous arrays

    with builder.if_then(use_copy, likely=False):
        # Allocate temporary scratchpad
        # XXX: should we use a stack-allocated array for very small
        # data sizes?
        allocsize = builder.mul(src.itemsize, src.nitems)
        data = context.nrt.allocate(builder, allocsize)
        voidptrty = data.type
        data = builder.bitcast(data, ptrty)
        builder.store(data, copy_data)

        # Copy source data into scratchpad
        intp_t = context.get_value_type(types.intp)

        with cgutils.loop_nest(builder, src_shapes, intp_t) as indices:
            src_ptr = cgutils.get_item_pointer2(builder, src_data,
                                                src_shapes, src_strides,
                                                srcty.layout, indices)
            dest_ptr = cgutils.get_item_pointer2(builder, data,
                                                 copy_shapes, copy_strides,
                                                 copy_layout, indices)
            builder.store(builder.load(src_ptr), dest_ptr)

    def src_getitem(source_indices):
        assert len(source_indices) == srcty.ndim
        src_ptr = cgutils.alloca_once(builder, ptrty)
        with builder.if_else(use_copy, likely=False) as (if_copy, otherwise):
            with if_copy:
                builder.store(
                    cgutils.get_item_pointer2(builder, builder.load(copy_data),
                                              copy_shapes, copy_strides,
                                              copy_layout, source_indices,
                                              wraparound=False),
                    src_ptr)
            with otherwise:
                builder.store(
                    cgutils.get_item_pointer2(builder, src_data,
                                              src_shapes, src_strides,
                                              srcty.layout, source_indices,
                                              wraparound=False),
                    src_ptr)
        return load_item(context, builder, srcty, builder.load(src_ptr))

    def src_cleanup():
        # Deallocate memory
        with builder.if_then(use_copy, likely=False):
            data = builder.load(copy_data)
            data = builder.bitcast(data, voidptrty)
            context.nrt.free(builder, data)

    return src_getitem, src_cleanup