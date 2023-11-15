    def _execute_agg(cls, ctx, op: "DataFrameGroupByAgg"):
        xdf = cudf if op.gpu else pd
        out_chunk = op.outputs[0]
        col_value = out_chunk.columns_value.to_pandas() if hasattr(out_chunk, 'columns_value') else None

        in_data_tuple = ctx[op.inputs[0].key]
        in_data_list = []
        for in_data in in_data_tuple:
            if isinstance(in_data, xdf.Series) and op.output_types[0] == OutputType.dataframe:
                in_data = cls._series_to_df(in_data, op.gpu)
            in_data_list.append(in_data)
        in_data_tuple = tuple(in_data_list)
        in_data_dict = cls._pack_inputs(op.agg_funcs, in_data_tuple)

        for _input_key, _map_func_name, agg_func_name, custom_reduction, \
                output_key, _output_limit, kwds in op.agg_funcs:
            if agg_func_name == 'custom_reduction':
                input_obj = tuple(cls._get_grouped(op, o, ctx) for o in in_data_dict[output_key])
                in_data_dict[output_key] = cls._do_custom_agg(op, custom_reduction, *input_obj)[0]
            else:
                input_obj = cls._get_grouped(op, in_data_dict[output_key], ctx)
                in_data_dict[output_key] = cls._do_predefined_agg(input_obj, agg_func_name, **kwds)

        aggs = []
        for input_keys, _output_key, func_name, cols, func in op.post_funcs:
            if cols is None:
                func_inputs = [in_data_dict[k] for k in input_keys]
            else:
                func_inputs = [in_data_dict[k][cols] for k in input_keys]

            if func_inputs[0].ndim == 2 and len(set(inp.shape[1] for inp in func_inputs)) > 1:
                common_cols = func_inputs[0].columns
                for inp in func_inputs[1:]:
                    common_cols = common_cols.join(inp.columns, how='inner')
                func_inputs = [inp[common_cols] for inp in func_inputs]

            agg_df = func(*func_inputs, gpu=op.is_gpu())
            if isinstance(agg_df, np.ndarray):
                agg_df = xdf.DataFrame(agg_df, index=func_inputs[0].index)

            new_cols = None
            if out_chunk.ndim == 2 and col_value is not None:
                if col_value.nlevels > agg_df.columns.nlevels:
                    new_cols = xdf.MultiIndex.from_product([agg_df.columns, [func_name]])
                elif agg_df.shape[-1] == 1 and func_name in col_value:
                    new_cols = xdf.Index([func_name])
            aggs.append((agg_df, new_cols))

        for agg_df, new_cols in aggs:
            if new_cols is not None:
                agg_df.columns = new_cols
        aggs = [item[0] for item in aggs]

        if out_chunk.ndim == 2:
            result = xdf.concat(aggs, axis=1)
            if not op.groupby_params.get('as_index', True) \
                    and col_value.nlevels == result.columns.nlevels:
                result.reset_index(inplace=True, drop=result.index.name in result.columns)
            result = result.reindex(col_value, axis=1)

            if result.ndim == 2 and len(result) == 0:
                result = result.astype(out_chunk.dtypes)
        else:
            result = xdf.concat(aggs)
            if result.ndim == 2:
                result = result.iloc[:, 0]
            result.name = out_chunk.name

        ctx[out_chunk.key] = result