    def _execute_reduce(cls, ctx, op):
        out_chunk = op.outputs[0]
        input_keys, _ = get_shuffle_input_keys_idxes(op.inputs[0])
        if getattr(ctx, 'running_mode', None) == RunningMode.distributed:
            raw_inputs = [ctx.pop((input_key, op.shuffle_key)) for input_key in input_keys]
        else:
            raw_inputs = [ctx[(input_key, op.shuffle_key)] for input_key in input_keys]

        xdf = pd if isinstance(raw_inputs[0], (pd.DataFrame, pd.Series)) else cudf
        if xdf is pd:
            concat_values = xdf.concat(raw_inputs, axis=op.axis, copy=False)
        else:
            concat_values = xdf.concat(raw_inputs, axis=op.axis)
        del raw_inputs[:]

        if isinstance(concat_values, xdf.DataFrame):
            concat_values.drop(_PSRS_DISTINCT_COL, axis=1, inplace=True, errors='ignore')

            col_index_dtype = out_chunk.columns_value.to_pandas().dtype
            if concat_values.columns.dtype != col_index_dtype:
                concat_values.columns = concat_values.columns.astype(col_index_dtype)

        if op.sort_type == 'sort_values':
            ctx[op.outputs[0].key] = execute_sort_values(concat_values, op)
        else:
            ctx[op.outputs[0].key] = execute_sort_index(concat_values, op)