    def execute(cls, ctx, op):
        a = ctx[op.inputs[0].key]

        if op.sort_type == 'sort_values':
            ctx[op.outputs[0].key] = res = execute_sort_values(a, op)
        else:
            ctx[op.outputs[0].key] = res = execute_sort_index(a, op)

        by = op.by
        add_distinct_col = bool(int(os.environ.get('PSRS_DISTINCT_COL', '0'))) \
            or getattr(ctx, 'running_mode', None) == RunningMode.distributed
        if add_distinct_col and isinstance(a, pd.DataFrame) and op.sort_type == 'sort_values':
            # when running under distributed mode, we introduce an extra column
            # to make sure pivots are distinct
            chunk_idx = op.inputs[0].index[0]
            distinct_col = _PSRS_DISTINCT_COL if a.columns.nlevels == 1 \
                else (_PSRS_DISTINCT_COL,) + ('',) * (a.columns.nlevels - 1)
            res[distinct_col] = np.arange(chunk_idx << 32, (chunk_idx << 32) + len(a), dtype=np.int64)
            by = list(by) + [distinct_col]

        n = op.n_partition
        if a.shape[op.axis] < n:
            num = n // a.shape[op.axis] + 1
            res = execute_sort_values(pd.concat([res] * num), op, by=by)
        w = int(res.shape[op.axis] // n)

        slc = (slice(None),) * op.axis + (slice(0, n * w, w),)
        if op.sort_type == 'sort_values':
            # do regular sample
            if op.by is not None:
                ctx[op.outputs[-1].key] = res[by].iloc[slc]
            else:
                ctx[op.outputs[-1].key] = res.iloc[slc]
        else:
            # do regular sample
            ctx[op.outputs[-1].key] = res.iloc[slc]