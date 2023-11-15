    def _groupby_dict_reduce(
        self, by, axis, agg_func, agg_args, agg_kwargs, groupby_kwargs, drop=False
    ):
        map_dict = {}
        reduce_dict = {}
        rename_columns = any(
            not isinstance(fn, str) and isinstance(fn, Iterable)
            for fn in agg_func.values()
        )
        for col, col_funcs in agg_func.items():
            if not rename_columns:
                map_dict[col], reduce_dict[col] = groupby_reduce_functions[col_funcs]
                continue

            if isinstance(col_funcs, str):
                col_funcs = [col_funcs]

            map_fns = []
            for i, fn in enumerate(col_funcs):
                if not isinstance(fn, str) and isinstance(fn, Iterable):
                    new_col_name, func = fn
                elif isinstance(fn, str):
                    new_col_name, func = fn, fn
                else:
                    raise TypeError

                map_fns.append((new_col_name, groupby_reduce_functions[func][0]))
                reduced_col_name = (
                    (*col, new_col_name)
                    if isinstance(col, tuple)
                    else (col, new_col_name)
                )
                reduce_dict[reduced_col_name] = groupby_reduce_functions[func][1]
            map_dict[col] = map_fns
        return GroupbyReduceFunction.register(map_dict, reduce_dict)(
            query_compiler=self,
            by=by,
            axis=axis,
            groupby_args=groupby_kwargs,
            map_args=agg_kwargs,
            reduce_args=agg_kwargs,
            numeric_only=False,
            drop=drop,
        )