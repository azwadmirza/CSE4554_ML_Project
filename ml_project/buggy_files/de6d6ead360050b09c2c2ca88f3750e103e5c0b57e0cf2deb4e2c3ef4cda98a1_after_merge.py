    def execute(cls, ctx, op):
        (a, b), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            if not op.sparse and is_sparse_module(xp):
                # tell sparse to do calculation on numpy or cupy matmul
                ctx[op.outputs[0].key] = xp.matmul(a, b, sparse=False)
            else:
                try:
                    # `np.matmul` support `order` argument in version 1.16
                    ctx[op.outputs[0].key] = xp.matmul(a, b, casting=op.casting, order=op.order)
                except TypeError:  # pragma: no cover
                    ctx[op.outputs[0].key] = xp.matmul(a, b).astype(dtype=op.dtype,
                                                                    casting=op.casting, order=op.order)