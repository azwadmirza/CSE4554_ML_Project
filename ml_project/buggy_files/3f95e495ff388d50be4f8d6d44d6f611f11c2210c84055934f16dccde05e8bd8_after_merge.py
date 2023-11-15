    def execute(cls, ctx, op):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            a = op.lhs if np.isscalar(op.lhs) else inputs[0]
            b = op.rhs if np.isscalar(op.rhs) else inputs[-1]

            ctx[op.outputs[0].key] = xp.isclose(a, b, atol=op.atol, rtol=op.rtol,
                                                equal_nan=op.equal_nan)