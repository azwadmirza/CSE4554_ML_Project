    def execute(cls, ctx, op):
        func_name = getattr(cls, '_func_name')
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        func = getattr(xp, func_name)

        with device(device_id):
            kw = {'casting': op.casting} if op.out else {}

            inputs_iter = iter(inputs)
            lhs = op.lhs if np.isscalar(op.lhs) else next(inputs_iter)
            rhs = op.rhs if np.isscalar(op.rhs) else next(inputs_iter)
            if op.out:
                kw['out'] = next(inputs_iter).copy()
            if op.where:
                kw['where'] = next(inputs_iter)
            kw['order'] = op.order

            with np.errstate(**op.err):
                ctx[op.outputs[0].key] = _handle_out_dtype(func(lhs, rhs, **kw), op.dtype)