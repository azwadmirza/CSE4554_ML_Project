    def memory_usage(self, **kwargs):
        """Returns the memory usage of each column.

        Returns:
            A new QueryCompiler object containing the memory usage of each column.
        """

        def memory_usage_builder(df, **kwargs):
            return df.memory_usage(**kwargs)

        def sum_memory_usage(df):
            return df.sum()

        map_func = self._build_mapreduce_func(memory_usage_builder, **kwargs)
        reduce_func = self._build_mapreduce_func(sum_memory_usage)
        return self._full_reduce(0, map_func, reduce_func)