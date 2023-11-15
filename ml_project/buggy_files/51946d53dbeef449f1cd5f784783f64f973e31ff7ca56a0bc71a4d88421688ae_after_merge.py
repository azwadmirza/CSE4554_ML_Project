    def _execute_combine_with_count(cls, ctx, op, reduction_func=None):
        # Execution with specified `min_count` in the combine stage

        xdf = cudf if op.gpu else pd
        in_data, concat_count = ctx[op.inputs[0].key]
        count = concat_count.sum(axis=op.axis)
        r = cls._execute_reduction(in_data, op, reduction_func=reduction_func)
        if isinstance(in_data, xdf.Series):
            if op.output_types[0] == OutputType.series:
                r = xdf.Series([r])
                count = xdf.Series([count])
            ctx[op.outputs[0].key] = (r, count)
        else:
            # For dataframe, will keep dimensions for intermediate results.
            ctx[op.outputs[0].key] = (xdf.DataFrame(r), xdf.DataFrame(count)) if op.axis == 1 \
                else (xdf.DataFrame(r).transpose(), xdf.DataFrame(count).transpose())