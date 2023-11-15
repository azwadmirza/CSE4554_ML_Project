    def execute_map(cls, ctx, op):
        chunk = op.outputs[0]
        df = ctx[op.inputs[0].key]
        shuffle_on = op.shuffle_on

        if shuffle_on is not None:
            # shuffle on field may be resident in index
            to_reset_index_names = []
            if not isinstance(shuffle_on, (list, tuple)):
                if shuffle_on not in df.dtypes:
                    to_reset_index_names.append(shuffle_on)
            else:
                for son in shuffle_on:
                    if son not in df.dtypes:
                        to_reset_index_names.append(shuffle_on)
            if len(to_reset_index_names) > 0:
                df = df.reset_index(to_reset_index_names)

        filters = hash_dataframe_on(df, shuffle_on, op.index_shuffle_size)

        # shuffle on index
        for index_idx, index_filter in enumerate(filters):
            group_key = ','.join([str(index_idx), str(chunk.index[1])])
            if index_filter is not None and index_filter is not list():
                ctx[(chunk.key, group_key)] = df.loc[index_filter]
            else:
                ctx[(chunk.key, group_key)] = None