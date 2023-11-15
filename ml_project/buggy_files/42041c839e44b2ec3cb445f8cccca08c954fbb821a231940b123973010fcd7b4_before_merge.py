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
        else:
            result = in_data.transform(op.func, *op.args, **op.kwds)

        if result.ndim == 2:
            result = result.astype(op.outputs[0].dtypes, copy=False)
        else:
            result = result.astype(op.outputs[0].dtype, copy=False)
        ctx[op.outputs[0].key] = result