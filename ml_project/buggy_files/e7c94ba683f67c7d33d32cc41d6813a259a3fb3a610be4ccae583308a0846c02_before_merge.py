    def _execute_dataframe_map(cls, ctx, op):
        a, pivots = [ctx[c.key] for c in op.inputs]
        out = op.outputs[0]

        if isinstance(a, pd.DataFrame):
            # use numpy.searchsorted to find split positions.
            by = op.by

            distinct_col = _PSRS_DISTINCT_COL if a.columns.nlevels == 1 \
                else (_PSRS_DISTINCT_COL,) + ('',) * (a.columns.nlevels - 1)
            if _PSRS_DISTINCT_COL in a.columns:
                by += [distinct_col]

            records = a[by].to_records(index=False)
            p_records = pivots.to_records(index=False)
            if op.ascending:
                poses = records.searchsorted(p_records, side='right')
            else:
                poses = len(records) - records[::-1].searchsorted(p_records, side='right')
            del records, p_records

            poses = (None,) + tuple(poses) + (None,)
            for i in range(op.n_partition):
                values = a.iloc[poses[i]: poses[i + 1]]
                ctx[(out.key, str(i))] = values
        else:  # pragma: no cover
            # for cudf, find split positions in loops.
            if op.ascending:
                pivots.append(a.iloc[-1][op.by])
                for i in range(op.n_partition):
                    selected = a
                    for label in op.by:
                        selected = selected.loc[a[label] <= pivots.iloc[i][label]]
                    ctx[(out.key, str(i))] = selected
            else:
                pivots.append(a.iloc[-1][op.by])
                for i in range(op.n_partition):
                    selected = a
                    for label in op.by:
                        selected = selected.loc[a[label] >= pivots.iloc[i][label]]
                    ctx[(out.key, str(i))] = selected