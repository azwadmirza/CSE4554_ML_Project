    def execute(cls, ctx, op: "RemoteFunction"):
        from ..session import Session

        session = ctx.get_current_session()
        prev_default_session = Session.default

        mapping = {inp: ctx[inp.key] for inp, prepare_inp
                   in zip(op.inputs, op.prepare_inputs) if prepare_inp}
        for to_search in [op.function_args, op.function_kwargs]:
            tileable_placeholders = find_objects(to_search, _TileablePlaceholder)
            for ph in tileable_placeholders:
                mapping[ph] = ph.tileable

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