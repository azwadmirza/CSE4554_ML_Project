    def execute(cls, ctx, op):
        (a, b), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            ctx[op.outputs[0].key] = xp.isclose(a, b, atol=op.atol, rtol=op.rtol,
                                                equal_nan=op.equal_nan)