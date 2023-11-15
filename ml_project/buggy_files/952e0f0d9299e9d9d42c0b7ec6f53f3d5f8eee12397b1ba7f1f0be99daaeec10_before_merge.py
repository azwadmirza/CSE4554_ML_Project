def _getitem_array_generic(context, builder, return_type, aryty, ary,
                           index_types, indices):
    """
    Return the result of indexing *ary* with the given *indices*,
    returning either a scalar or a view.
    """
    dataptr, view_shapes, view_strides = \
        basic_indexing(context, builder, aryty, ary, index_types, indices)

    if isinstance(return_type, types.Buffer):
        # Build array view
        retary = make_view(context, builder, aryty, ary, return_type,
                           dataptr, view_shapes, view_strides)
        return retary._getvalue()
    else:
        # Load scalar from 0-d result
        assert not view_shapes
        return load_item(context, builder, aryty, dataptr)