    def execute(cls, ctx, op):
        inputs = [ctx[c.key] for c in op.inputs if len(ctx[c.key]) > 0]
        if len(inputs) == 0:
            # corner case: nothing sampled, we need to do nothing
            ctx[op.outputs[-1].key] = ctx[op.inputs[0].key]
            return

        xdf = pd if isinstance(inputs[0], (pd.DataFrame, pd.Series)) else cudf

        a = xdf.concat(inputs, axis=op.axis)
        p = len(inputs)
        assert a.shape[op.axis] == p * len(op.inputs)

        slc = np.linspace(p - 1, a.shape[op.axis] - 1,
                          num=len(op.inputs) - 1, endpoint=False).astype(int)
        if op.axis == 1:
            slc = (slice(None), slc)
        if op.sort_type == 'sort_values':
            a = execute_sort_values(a, op, inplace=False)
            ctx[op.outputs[-1].key] = a.iloc[slc]
        else:
            a = execute_sort_index(a, op, inplace=False)
            ctx[op.outputs[-1].key] = a.index[slc]