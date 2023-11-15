    def execute(cls, ctx, op):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs if len(ctx[c.key]) > 0], device=op.device, ret_extra=True)

        with device(device_id):
            a = xp.concatenate(inputs, axis=op.axis)
            p = len(inputs)
            assert a.shape[op.axis] == p * len(op.inputs)

            if op.kind is not None:
                # sort
                _sort(a, op, xp, inplace=True)
            else:
                # prepare for sampling via `partition`
                kth = xp.linspace(p - 1, a.shape[op.axis] - 1,
                                  num=p - 1, endpoint=False).astype(int)
                a.partition(kth, axis=op.axis)

            select = xp.linspace(p - 1, a.shape[op.axis] - 1,
                                 num=len(op.inputs) - 1, endpoint=False).astype(int)
            slc = (slice(None),) * op.axis + (select,)
            ctx[op.outputs[0].key] = a[slc]