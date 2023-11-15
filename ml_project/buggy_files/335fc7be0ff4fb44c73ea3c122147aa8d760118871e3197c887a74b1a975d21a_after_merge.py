    def execute_agg(cls, ctx, op):
        (input_chunk,), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)
        axis = cls.get_axis(op.axis)
        func_name = getattr(cls, '_func_name', None)
        reduce_func = getattr(xp, func_name)
        out = op.outputs[0]
        with device(device_id):
            if input_chunk.size == 0 and op.keepdims:
                # input chunk is empty, when keepdims is True, return itself
                ret = input_chunk
            elif "dtype" in inspect.getfullargspec(reduce_func).args:
                ret = reduce_func(input_chunk, axis=axis,
                                  dtype=op.dtype,
                                  keepdims=bool(op.keepdims))
            else:
                ret = reduce_func(input_chunk, axis=axis,
                                  keepdims=bool(op.keepdims))

            if hasattr(ret, 'astype'):
                # for non-object dtype
                ret = ret.astype(op.dtype, order=out.order.value, copy=False)
            ctx[out.key] = ret