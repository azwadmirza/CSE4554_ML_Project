    def execute_map(cls, ctx, op):
        arg_axis = cls.get_arg_axis(op.axis, op.inputs[0].ndim)
        (in_chunk,), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        func_name = getattr(cls, '_func_name')
        agg_func_name = getattr(cls, '_agg_func_name')
        arg_func = getattr(xp, func_name)
        agg_func_name = getattr(xp, agg_func_name)

        offset = op.offset
        chunk = op.outputs[0]
        with device(device_id):
            vals = agg_func_name(in_chunk, axis=arg_axis)
            if hasattr(vals, 'reshape'):
                vals = vals.reshape(chunk.shape)
            try:
                arg = arg_func(in_chunk, axis=arg_axis)
                if hasattr(arg, 'reshape'):
                    arg = arg.reshape(chunk.shape)
            except ValueError:
                # handle all NaN
                arg = arg_func(xp.where(xp.isnan(in_chunk), np.inf, in_chunk),
                               axis=arg_axis).reshape(chunk.shape)

            if arg_axis is None:
                if xp == cp:
                    # we need to copy to do cpu computation, then copy back to gpu
                    # cuz unravel_index and ravel_multi_index are not implemented in cupy
                    in_chunk = in_chunk.get()

                total_shape = op.total_shape
                ind = np.unravel_index(arg.ravel()[0], in_chunk.shape)
                total_ind = tuple(o + i for (o, i) in zip(offset, ind))
                res = np.ravel_multi_index(total_ind, total_shape)

                if xp == cp:
                    # copy back
                    with xp.cuda.Device(in_chunk.device.id):
                        arg[:] = xp.asarray(res)
                else:
                    arg[:] = res
            else:
                arg += offset
            ctx[op.outputs[0].key] = (vals, arg)