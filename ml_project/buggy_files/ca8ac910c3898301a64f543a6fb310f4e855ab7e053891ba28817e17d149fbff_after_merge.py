    def _execute_dataframe_map(cls, ctx, op):
        a, pivots = [ctx[c.key] for c in op.inputs]
        out = op.outputs[0]

        if len(a) == 0:
            # when the chunk is empty, no slices can be produced
            for i in range(op.n_partition):
                ctx[(out.key, str(i))] = a
            return

        # use numpy.searchsorted to find split positions.
        by = op.by

        distinct_col = _PSRS_DISTINCT_COL if a.columns.nlevels == 1 \
            else (_PSRS_DISTINCT_COL,) + ('',) * (a.columns.nlevels - 1)
        if distinct_col in a.columns:
            by = list(by) + [distinct_col]

        try:
            poses = cls._calc_poses(a[by], pivots, op.ascending)
        except TypeError:
            poses = cls._calc_poses(
                a[by].fillna(_largest), pivots.fillna(_largest), op.ascending)

        poses = (None,) + tuple(poses) + (None,)
        for i in range(op.n_partition):
            values = a.iloc[poses[i]: poses[i + 1]]
            ctx[(out.key, str(i))] = values