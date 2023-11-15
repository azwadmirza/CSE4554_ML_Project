def _getitem_array1d(context, builder, arrayty, array, idx, wraparound):
    """
    Look up and return an element from a 1D array.
    """
    ptr = cgutils.get_item_pointer(builder, arrayty, array, [idx],
                                   wraparound=wraparound)
    return load_item(context, builder, arrayty, ptr)