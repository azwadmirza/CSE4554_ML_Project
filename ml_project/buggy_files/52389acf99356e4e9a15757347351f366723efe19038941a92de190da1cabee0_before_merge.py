    def _execute_map(cls, ctx, op):
        xdf = cudf if op.gpu else pd
        in_data = ctx[op.inputs[0].key]
        if isinstance(in_data, pd.Series):
            count = in_data.count()
        else:
            count = in_data.count(axis=op.axis, numeric_only=op.numeric_only)
        r = cls._execute_reduction(in_data, op, reduction_func='sum')
        avg = cls._keep_dim(r / count, op)

        kwargs = dict(axis=op.axis, skipna=op.skipna)
        if op.numeric_only:
            in_data = in_data[avg.columns]
        avg = avg if np.isscalar(avg) else np.array(avg)
        var_square = ((in_data.subtract(avg)) ** 2).sum(**kwargs)

        if isinstance(in_data, xdf.Series):
            ctx[op.outputs[0].key] = (r, count, var_square)
        else:
            ctx[op.outputs[0].key] = tuple(cls._keep_dim(df, op) for df in [r, count, var_square])