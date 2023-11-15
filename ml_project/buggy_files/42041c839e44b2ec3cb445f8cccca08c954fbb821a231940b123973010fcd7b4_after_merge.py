    def execute(cls, ctx, op):
        in_data = ctx[op.inputs[0].key]
        out_chunk = op.outputs[0]

        if not in_data:
            if op.output_types[0] == OutputType.dataframe:
                ctx[op.outputs[0].key] = build_empty_df(out_chunk.dtypes)
            else:
                ctx[op.outputs[0].key] = build_empty_series(out_chunk.dtype)
            return

        if op.call_agg:
            result = in_data.agg(op.func, *op.args, **op.kwds)
        elif in_data.shape[0] > 0:
            # cannot perform groupby-transform over empty dataframe
            result = in_data.transform(op.func, *op.args, **op.kwds)
        else:
            if out_chunk.ndim == 2:
                result = pd.DataFrame(columns=out_chunk.dtypes.index)
            else:
                result = pd.Series([], name=out_chunk.name, dtype=out_chunk.dtype)

        if result.ndim == 2:
            result = result.astype(out_chunk.dtypes, copy=False)
        else:
            result = result.astype(out_chunk.dtype, copy=False)
        ctx[op.outputs[0].key] = result