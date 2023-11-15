    def execute(cls, ctx, op: "GroupByCumReductionOperand"):
        in_data = ctx[op.inputs[0].key]
        out_chunk = op.outputs[0]

        if not in_data or in_data.empty:
            ctx[out_chunk.key] = build_empty_df(out_chunk.dtypes) \
                if op.output_types[0] == OutputType.dataframe \
                else build_empty_series(out_chunk.dtype, name=out_chunk.name)
            return

        func_name = getattr(op, '_func_name')
        if func_name == 'cumcount':
            ctx[out_chunk.key] = in_data.cumcount(ascending=op.ascending)
        else:
            result = getattr(in_data, func_name)(axis=op.axis)
            if result.ndim == 2:
                ctx[out_chunk.key] = result.astype(out_chunk.dtypes, copy=False)
            else:
                ctx[out_chunk.key] = result.astype(out_chunk.dtype, copy=False)