    def execute(cls, ctx, op):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            kw = {'casting': op.casting} if op.out else {}

            if op.out and op.where:
                inputs, kw['out'], kw['where'] = inputs[:-2], inputs[-2].copy(), inputs[-1]
            elif op.out:
                inputs, kw['out'] = inputs[:-1], inputs[-1].copy()
            elif op.where:
                inputs, kw['where'] = inputs[:-1], inputs[-1]

            with np.errstate(**op.err):
                if op.is_gpu():
                    ret = cls._execute_gpu(op, xp, inputs[0], **kw)
                else:
                    ret = cls._execute_cpu(op, xp, inputs[0], **kw)
                ctx[op.outputs[0].key] = _handle_out_dtype(ret, op.dtype)