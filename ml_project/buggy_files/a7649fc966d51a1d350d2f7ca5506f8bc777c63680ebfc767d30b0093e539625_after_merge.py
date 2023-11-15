    def execute(cls, ctx, op):
        (a,), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        if len(a) == 0:
            # when chunk is empty, return the empty chunk itself
            ctx[op.outputs[0].key] = ctx[op.outputs[-1].key] = a
            return

        with device(device_id):
            n = op.n_partition
            w = a.shape[op.axis] * 1.0 / (n + 1)
            if not op.return_indices:
                if op.kind is not None:
                    # sort
                    res = ctx[op.outputs[0].key] = _sort(a, op, xp)
                else:
                    # do not sort, prepare for sample by `xp.partition`
                    kth = xp.linspace(max(w - 1, 0), a.shape[op.axis] - 1,
                                      num=n, endpoint=False).astype(int)
                    ctx[op.outputs[0].key] = res = xp.partition(
                        a, kth, axis=op.axis, order=op.order)
            else:
                if op.kind is not None:
                    # argsort
                    indices = _argsort(a, op, xp)
                else:
                    # do not sort, use `xp.argpartition`
                    kth = xp.linspace(max(w - 1, 0), a.shape[op.axis] - 1,
                                      num=n, endpoint=False).astype(int)
                    indices = xp.argpartition(
                        a, kth, axis=op.axis, order=op.order)
                ctx[op.outputs[0].key] = res = xp.take_along_axis(a, indices, op.axis)
                ctx[op.outputs[1].key] = op.axis_offset + indices

            # do regular sample
            if op.order is not None:
                res = res[op.order]
            slc = xp.linspace(max(w - 1, 0), a.shape[op.axis] - 1,
                              num=n, endpoint=False).astype(int)
            slc = (slice(None),) * op.axis + (slc,)
            ctx[op.outputs[-1].key] = res[slc]