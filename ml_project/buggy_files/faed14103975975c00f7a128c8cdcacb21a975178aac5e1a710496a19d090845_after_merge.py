    def assign_item(indices, valty, val):
        ptr = cgutils.get_item_pointer2(context, builder, data, shapes, strides,
                                        arrty.layout, indices, wraparound=False)
        val = context.cast(builder, val, valty, arrty.dtype)
        store_item(context, builder, arrty, val, ptr)