def get_item_pointer(context, builder, aryty, ary, inds, wraparound=False,
                     boundscheck=False):
    # Set boundscheck=True for any pointer access that should be
    # boundschecked. do_boundscheck() will handle enabling or disabling the
    # actual boundschecking based on the user config.
    shapes = unpack_tuple(builder, ary.shape, count=aryty.ndim)
    strides = unpack_tuple(builder, ary.strides, count=aryty.ndim)
    return get_item_pointer2(context, builder, data=ary.data, shape=shapes,
                             strides=strides, layout=aryty.layout, inds=inds,
                             wraparound=wraparound, boundscheck=boundscheck)