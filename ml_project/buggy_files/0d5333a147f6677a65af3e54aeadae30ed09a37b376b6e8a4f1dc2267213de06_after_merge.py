    def _is_monotonic(self, func_type=None):
        funcs = {
            "increasing": lambda df: df.is_monotonic_increasing,
            "decreasing": lambda df: df.is_monotonic_decreasing,
        }

        monotonic_fn = funcs.get(func_type, funcs["increasing"])

        def is_monotonic_map(df):
            df = df.squeeze(axis=1)
            return [monotonic_fn(df), df.iloc[0], df.iloc[len(df) - 1]]

        def is_monotonic_reduce(df):
            df = df.squeeze(axis=1)

            common_case = df[0].all()
            left_edges = df[1]
            right_edges = df[2]

            edges_list = []
            for i in range(len(left_edges)):
                edges_list.extend([left_edges.iloc[i], right_edges.iloc[i]])

            edge_case = monotonic_fn(pandas.Series(edges_list))
            return [common_case and edge_case]

        return MapReduceFunction.register(
            is_monotonic_map, is_monotonic_reduce, axis=0
        )(self)