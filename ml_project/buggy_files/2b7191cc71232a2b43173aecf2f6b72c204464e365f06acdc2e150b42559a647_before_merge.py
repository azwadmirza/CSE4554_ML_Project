    def _execute_map_with_count(cls, ctx, op, reduction_func=None):
        # Execution with specified `min_count` in the map stage

        xdf = cudf if op.gpu else pd
        in_data = ctx[op.inputs[0].key]
        if isinstance(in_data, pd.Series):
            count = in_data.count()
        else:
            count = in_data.count(axis=op.axis, numeric_only=op.numeric_only)
        r = cls._execute_reduction(in_data, op, reduction_func=reduction_func)
        if isinstance(in_data, xdf.Series):
            ctx[op.outputs[0].key] = (r, count)
        else:
            # For dataframe, will keep dimensions for intermediate results.
            ctx[op.outputs[0].key] = (xdf.DataFrame(r), xdf.DataFrame(count)) if op.axis == 1 \
                else (xdf.DataFrame(r).transpose(), xdf.DataFrame(count).transpose())