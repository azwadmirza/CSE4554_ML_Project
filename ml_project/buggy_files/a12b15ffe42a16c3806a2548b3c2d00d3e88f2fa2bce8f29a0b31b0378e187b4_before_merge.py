    def execute_map(cls, ctx, op):
        is_dataframe_obj = op.is_dataframe_obj
        by = op.by
        chunk = op.outputs[0]
        df = ctx[op.inputs[0].key]

        deliver_by = False  # output by for the upcoming process
        if isinstance(by, list):
            new_by = []
            for v in by:
                if isinstance(v, Base):
                    deliver_by = True
                    new_by.append(ctx[v.key])
                else:
                    new_by.append(v)
            by = new_by

        if isinstance(by, list) or callable(by):
            on = by
        else:
            on = None

        if isinstance(df, tuple):
            filters = hash_dataframe_on(df[0], on, op.shuffle_size, level=op.level)
        else:
            filters = hash_dataframe_on(df, on, op.shuffle_size, level=op.level)

        for index_idx, index_filter in enumerate(filters):
            if is_dataframe_obj:
                group_key = ','.join([str(index_idx), str(chunk.index[1])])
            else:
                group_key = str(index_idx)

            if deliver_by:
                filtered_by = []
                for v in by:
                    if isinstance(v, pd.Series):
                        filtered_by.append(v.loc[index_filter])
                    else:
                        filtered_by.append(v)
                if isinstance(df, tuple):
                    ctx[(chunk.key, group_key)] = tuple(x.loc[index_filter] for x in df) \
                        + (filtered_by, deliver_by)
                else:
                    ctx[(chunk.key, group_key)] = (df.loc[index_filter], filtered_by, deliver_by)
            else:
                if isinstance(df, tuple):
                    ctx[(chunk.key, group_key)] = tuple(x.loc[index_filter] for x in df) + (deliver_by,)
                else:
                    ctx[(chunk.key, group_key)] = df.loc[index_filter]