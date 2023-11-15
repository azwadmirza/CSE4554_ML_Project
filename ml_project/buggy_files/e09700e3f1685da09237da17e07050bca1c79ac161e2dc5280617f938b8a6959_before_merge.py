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