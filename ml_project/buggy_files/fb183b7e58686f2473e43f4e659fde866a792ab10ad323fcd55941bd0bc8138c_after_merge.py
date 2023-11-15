    def _get_grouped(cls, op: "DataFrameGroupByAgg", df, ctx, copy=False, grouper=None):
        if copy:
            df = df.copy()

        params = op.groupby_params.copy()
        params.pop('as_index', None)
        selection = params.pop('selection', None)

        if grouper is not None:
            params['by'] = grouper
            params.pop('level', None)
        elif isinstance(params.get('by'), list):
            new_by = []
            for v in params['by']:
                if isinstance(v, Base):
                    new_by.append(ctx[v.key])
                else:
                    new_by.append(v)
            params['by'] = new_by

        if op.stage == OperandStage.agg:
            grouped = df.groupby(**params)
        else:
            # for the intermediate phases, do not sort
            params['sort'] = False
            grouped = df.groupby(**params)

        if selection is not None:
            grouped = grouped[selection]
        return grouped