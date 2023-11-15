    def execute(cls, ctx, op):
        (a, b), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            if not op.sparse and is_sparse_module(xp):
                # tell sparse to do calculation on numpy or cupy matmul
                ctx[op.outputs[0].key] = xp.matmul(a, b, sparse=False)
            else:
                ctx[op.outputs[0].key] = xp.matmul(a, b, casting=op.casting, order=op.order)