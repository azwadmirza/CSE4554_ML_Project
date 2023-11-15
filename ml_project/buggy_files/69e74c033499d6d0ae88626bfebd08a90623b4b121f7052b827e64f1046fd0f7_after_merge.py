    def execute(cls, ctx, op):
        a = ctx[op.inputs[0].key]

        if op.sort_type == 'sort_values':
            ctx[op.outputs[0].key] = res = execute_sort_values(a, op)
        else:
            ctx[op.outputs[0].key] = res = execute_sort_index(a, op)

        n = op.n_partition
        if a.shape[op.axis] < n:
            num = n // a.shape[op.axis] + 1
            res = execute_sort_values(pd.concat([a] * num), op)
        w = int(res.shape[op.axis] // n)

        slc = (slice(None),) * op.axis + (slice(0, n * w, w),)
        if op.sort_type == 'sort_values':
            # do regular sample
            if op.by is not None:
                ctx[op.outputs[-1].key] = res[op.by].iloc[slc]
            else:
                ctx[op.outputs[-1].key] = res.iloc[slc]
        else:
            # do regular sample
            ctx[op.outputs[-1].key] = res.iloc[slc]