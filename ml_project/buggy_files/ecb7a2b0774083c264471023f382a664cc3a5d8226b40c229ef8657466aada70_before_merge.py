    def memory_usage(self, **kwargs):
        """Returns the memory usage of each column.

        Returns:
            A new QueryCompiler object containing the memory usage of each column.
        """

        def memory_usage_builder(df, **kwargs):
            return df.memory_usage(**kwargs)

        func = self._build_mapreduce_func(memory_usage_builder, **kwargs)
        return self._full_axis_reduce(0, func)