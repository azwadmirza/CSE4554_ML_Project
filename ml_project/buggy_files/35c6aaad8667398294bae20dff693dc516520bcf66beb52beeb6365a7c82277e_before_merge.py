def _build_array(context, builder, array_ty, input_types, inputs):
    """Utility function to handle allocation of an implicit output array
    given the target context, builder, output array type, and a list of
    _ArrayHelper instances.
    """
    intp_ty = context.get_value_type(types.intp)
    def make_intp_const(val):
        return context.get_constant(types.intp, val)

    ZERO = make_intp_const(0)
    ONE = make_intp_const(1)

    src_shape = cgutils.alloca_once(builder, intp_ty, array_ty.ndim,
                                    "src_shape")
    dest_ndim = make_intp_const(array_ty.ndim)
    dest_shape = cgutils.alloca_once(builder, intp_ty, array_ty.ndim,
                                     "dest_shape")
    dest_shape_addrs = tuple(cgutils.gep_inbounds(builder, dest_shape, index)
                             for index in range(array_ty.ndim))

    # Initialize the destination shape with all ones.
    for dest_shape_addr in dest_shape_addrs:
        builder.store(ONE, dest_shape_addr)

    # For each argument, try to broadcast onto the destination shape,
    # mutating along any axis where the argument shape is not one and
    # the destination shape is one.
    for arg_number, arg in enumerate(inputs):
        if not hasattr(arg, "ndim"): # Skip scalar arguments
            continue
        arg_ndim = make_intp_const(arg.ndim)
        for index in range(arg.ndim):
            builder.store(arg.shape[index],
                          cgutils.gep_inbounds(builder, src_shape, index))
        arg_result = context.compile_internal(
            builder, _broadcast_onto, _broadcast_onto_sig,
            [arg_ndim, src_shape, dest_ndim, dest_shape])
        with cgutils.if_unlikely(builder,
                                 builder.icmp(lc.ICMP_SLT, arg_result, ONE)):
            msg = "unable to broadcast argument %d to output array" % (
                arg_number,)
            context.call_conv.return_user_exc(builder, ValueError, (msg,))

    real_array_ty = array_ty.as_array

    dest_shape_tup = tuple(builder.load(dest_shape_addr)
                           for dest_shape_addr in dest_shape_addrs)
    array_val = arrayobj._empty_nd_impl(context, builder, real_array_ty,
                                        dest_shape_tup)

    # Get the best argument to call __array_wrap__ on
    array_wrapper_index = select_array_wrapper(input_types)
    array_wrapper_ty = input_types[array_wrapper_index]
    try:
        # __array_wrap__(source wrapped array, out array) -> out wrapped array
        array_wrap = context.get_function('__array_wrap__',
                                          array_ty(array_wrapper_ty, real_array_ty))
    except NotImplementedError:
        # If it's the same priority as a regular array, assume we
        # should use the allocated array unchanged.
        if array_wrapper_ty.array_priority != types.Array.array_priority:
            raise
        out_val = array_val._getvalue()
    else:
        wrap_args = (inputs[array_wrapper_index].return_val, array_val._getvalue())
        out_val = array_wrap(builder, wrap_args)

    ndim = array_ty.ndim
    shape   = cgutils.unpack_tuple(builder, array_val.shape, ndim)
    strides = cgutils.unpack_tuple(builder, array_val.strides, ndim)
    return _ArrayHelper(context, builder, shape, strides, array_val.data,
                        array_ty.layout, array_ty.dtype, ndim,
                        out_val)