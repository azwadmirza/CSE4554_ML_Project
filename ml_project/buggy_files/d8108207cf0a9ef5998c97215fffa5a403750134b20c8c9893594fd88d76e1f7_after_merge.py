    def execute(cls, ctx, op):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            kw = {'casting': op.casting} if op.out else {}

            inputs_iter = iter(inputs)
            lhs = op.lhs if np.isscalar(op.lhs) else next(inputs_iter)
            rhs = op.rhs if np.isscalar(op.rhs) else next(inputs_iter)
            if op.out:
                kw['out'] = next(inputs_iter).copy()
            if op.where:
                kw['where'] = next(inputs_iter)

            with np.errstate(**op.err):
                if op.is_gpu():
                    ret = cls._execute_gpu(op, xp, lhs, rhs, **kw)
                else:
                    ret = cls._execute_cpu(op, xp, lhs, rhs, **kw)
                ctx[op.outputs[0].key] = _handle_out_dtype(ret, op.dtype)