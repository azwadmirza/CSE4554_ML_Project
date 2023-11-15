    def _execute_combine(cls, ctx, op):
        data, concat_count, var_square = ctx[op.inputs[0].key]
        xdf = cudf if op.gpu else pd

        count = concat_count.sum(axis=op.axis)
        r = cls._execute_reduction(data, op, reduction_func='sum')
        avg = cls._keep_dim(r / count, op)
        avg_diff = data / concat_count - avg

        kwargs = dict(axis=op.axis, skipna=op.skipna)
        reduced_var_square = var_square.sum(**kwargs) + (concat_count * avg_diff ** 2).sum(**kwargs)
        if isinstance(data, xdf.Series):
            if op.output_types[0] == OutputType.series and not isinstance(r, xdf.Series):
                r = xdf.Series([r])
                count = xdf.Series([count])
                reduced_var_square = xdf.Series([reduced_var_square])
            ctx[op.outputs[0].key] = (r, count, reduced_var_square)
        else:
            ctx[op.outputs[0].key] = tuple(cls._keep_dim(df, op) for df in [r, count, reduced_var_square])