    def execute(cls, ctx, op):
        inputs = [ctx[c.key] for c in op.inputs]
        xdf = pd if isinstance(inputs[0], (pd.DataFrame, pd.Series)) else cudf

        a = xdf.concat(inputs, axis=op.axis)
        p = len(inputs)
        assert a.shape[op.axis] == p ** 2

        slc = np.linspace(p - 1, a.shape[op.axis] - 1,
                          num=p - 1, endpoint=False).astype(int)
        if op.axis == 1:
            slc = (slice(None), slc)
        if op.sort_type == 'sort_values':
            a = execute_sort_values(a, op, inplace=False)
            ctx[op.outputs[-1].key] = a.iloc[slc]
        else:
            a = execute_sort_index(a, op, inplace=False)
            ctx[op.outputs[-1].key] = a.index[slc]