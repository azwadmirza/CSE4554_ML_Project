    def execute(cls, ctx, op):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            a = xp.concatenate(inputs, axis=op.axis)
            p = len(inputs)
            assert a.shape[op.axis] == p ** 2

            if op.kind is not None:
                # sort
                _sort(a, op, xp, inplace=True)
            else:
                # prepare for sampling via `partition`
                kth = xp.arange(p - 1, (p - 1) ** 2 + 1, p - 1)
                a.partition(kth, axis=op.axis)

            select = slice(p - 1, (p - 1) ** 2 + 1, p - 1)
            slc = (slice(None),) * op.axis + (select,)
            ctx[op.outputs[0].key] = a[slc]