def _build_elementwise(op):
    def _handle(ctx, chunk):
        inputs, device_id, xp = as_same_device(
            [ctx[c.key] for c in chunk.inputs], device=chunk.device, ret_extra=True)

        if isinstance(op, six.string_types):
            func = getattr(xp, op)
        else:
            func = op

        with device(device_id):
            kw = {'casting': chunk.op.casting} if chunk.op.out else {}

            if chunk.op.out and chunk.op.where:
                inputs, kw['out'], kw['where'] = inputs[:-2], inputs[-2].copy(), inputs[-1]
            elif chunk.op.out:
                inputs, kw['out'] = inputs[:-1], inputs[-1].copy()

            with np.errstate(**chunk.op.err):
                if len(inputs) == 1:
                    try:
                        ctx[chunk.key] = _handle_out_dtype(func(inputs[0], **kw), chunk.op.dtype)
                    except TypeError:
                        if kw.get('where') is None:
                            raise
                        out, where = kw.pop('out'), kw.pop('where')
                        ctx[chunk.key] = _handle_out_dtype(xp.where(where, func(inputs[0]), out),
                                                           chunk.op.dtype)
                else:
                    try:
                        if is_sparse_module(xp):
                            ctx[chunk.key] = _handle_out_dtype(reduce(lambda a, b: func(a, b, **kw), inputs),
                                                               chunk.op.dtype)
                        else:
                            if 'out' not in kw:
                                dest_value = xp.empty(chunk.shape, chunk.dtype)
                                kw['out'] = dest_value
                            ctx[chunk.key] = _handle_out_dtype(reduce(lambda a, b: func(a, b, **kw), inputs),
                                                               chunk.op.dtype)
                    except TypeError:
                        if kw.get('where') is None:
                            raise
                        out, where = kw.pop('out'), kw.pop('where')
                        ctx[chunk.key] = _handle_out_dtype(
                            xp.where(where, reduce(lambda a, b: func(a, b), inputs), out),
                            chunk.op.dtype)
    return _handle