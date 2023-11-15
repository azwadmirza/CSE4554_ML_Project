    def execute(cls, ctx, op: "GroupByCumReductionOperand"):
        in_data = ctx[op.inputs[0].key]
        out_df = op.outputs[0]

        if not in_data or in_data.empty:
            ctx[out_df.key] = build_empty_df(out_df.dtypes) \
                if op.output_types[0] == OutputType.dataframe else build_empty_series(out_df.dtype)
            return

        func_name = getattr(op, '_func_name')
        if func_name == 'cumcount':
            ctx[out_df.key] = in_data.cumcount(ascending=op.ascending)
        else:
            result = getattr(in_data, func_name)(axis=op.axis)
            if result.ndim == 2:
                ctx[out_df.key] = result.astype(out_df.dtypes, copy=False)
            else:
                ctx[out_df.key] = result.astype(out_df.dtype, copy=False)