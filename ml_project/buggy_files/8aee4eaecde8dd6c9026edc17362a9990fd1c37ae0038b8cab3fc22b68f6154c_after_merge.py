    def execute(cls, ctx, op: "RemoteFunction"):
        from ..session import Session

        session = ctx.get_current_session()
        prev_default_session = Session.default

        mapping = {inp: ctx[inp.key] for inp, prepare_inp
                   in zip(op.inputs, op.prepare_inputs) if prepare_inp}
        for to_search in [op.function_args, op.function_kwargs]:
            tileable_placeholders = find_objects(to_search, _TileablePlaceholder)
            for ph in tileable_placeholders:
                tileable = ph.tileable
                chunk_index_to_shape = dict()
                for chunk in tileable.chunks:
                    if any(np.isnan(s) for s in chunk.shape):
                        shape = ctx.get_chunk_metas([chunk.key], filter_fields=['chunk_shape'])[0][0]
                        chunk._shape = shape
                    chunk_index_to_shape[chunk.index] = chunk.shape
                if any(any(np.isnan(s) for s in ns) for ns in tileable._nsplits):
                    nsplits = calc_nsplits(chunk_index_to_shape)
                    tileable._nsplits = nsplits
                    tileable._shape = tuple(sum(ns) for ns in nsplits)
                mapping[ph] = tileable

        function = op.function
        function_args = replace_inputs(op.function_args, mapping)
        function_kwargs = replace_inputs(op.function_kwargs, mapping)

        # set session created from context as default one
        session.as_default()
        try:
            if isinstance(ctx, ContextBase):
                with ctx:
                    result = function(*function_args, **function_kwargs)
            else:
                result = function(*function_args, **function_kwargs)
        finally:
            # set back default session
            Session._set_default_session(prev_default_session)

        if op.n_output is None:
            ctx[op.outputs[0].key] = result
        else:
            if not isinstance(result, Iterable):
                raise TypeError('Specifying n_output={}, '
                                'but result is not iterable, got {}'.format(
                                 op.n_output, result))
            result = list(result)
            if len(result) != op.n_output:
                raise ValueError('Length of return value should be {}, '
                                 'got {}'.format(op.n_output, len(result)))
            for out, r in zip(op.outputs, result):
                ctx[out.key] = r