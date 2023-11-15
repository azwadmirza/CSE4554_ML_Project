    def value_counts(self, **kwargs):
        """
        Return a QueryCompiler of Series containing counts of unique values.

        Returns
        -------
        PandasQueryCompiler
        """
        if kwargs.get("bins", None) is not None:
            new_modin_frame = self._modin_frame._apply_full_axis(
                0, lambda df: df.squeeze(axis=1).value_counts(**kwargs)
            )
            return self.__constructor__(new_modin_frame)

        def map_func(df, *args, **kwargs):
            return df.squeeze(axis=1).value_counts(**kwargs).to_frame()

        def reduce_func(df, *args, **kwargs):
            normalize = kwargs.get("normalize", False)
            sort = kwargs.get("sort", True)
            ascending = kwargs.get("ascending", False)
            dropna = kwargs.get("dropna", True)

            try:
                result = df.squeeze(axis=1).groupby(df.index, sort=False).sum()
            # This will happen with Arrow buffer read-only errors. We don't want to copy
            # all the time, so this will try to fast-path the code first.
            except (ValueError):
                result = df.copy().squeeze(axis=1).groupby(df.index, sort=False).sum()

            if not dropna and np.nan in df.index:
                result = result.append(
                    pandas.Series(
                        [df.squeeze(axis=1).loc[[np.nan]].sum()], index=[np.nan]
                    )
                )
            if normalize:
                result = result / df.squeeze(axis=1).sum()

            result = result.sort_values(ascending=ascending) if sort else result

            # We want to sort both values and indices of the result object.
            # This function will sort indices for equal values.
            def sort_index_for_equal_values(result, ascending):
                """
                Sort indices for equal values of result object.

                Parameters
                ----------
                result : pandas.Series or pandas.DataFrame with one column
                    The object whose indices for equal values is needed to sort.
                ascending : boolean
                    Sort in ascending (if it is True) or descending (if it is False) order.

                Returns
                -------
                pandas.DataFrame
                    A new DataFrame with sorted indices.
                """
                is_range = False
                is_end = False
                i = 0
                new_index = np.empty(len(result), dtype=type(result.index))
                while i < len(result):
                    j = i
                    if i < len(result) - 1:
                        while result[result.index[i]] == result[result.index[i + 1]]:
                            i += 1
                            if is_range is False:
                                is_range = True
                            if i == len(result) - 1:
                                is_end = True
                                break
                    if is_range:
                        k = j
                        for val in sorted(
                            result.index[j : i + 1], reverse=not ascending
                        ):
                            new_index[k] = val
                            k += 1
                        if is_end:
                            break
                        is_range = False
                    else:
                        new_index[j] = result.index[j]
                    i += 1
                return pandas.DataFrame(
                    result, index=new_index, columns=["__reduced__"]
                )

            return sort_index_for_equal_values(result, ascending)

        return MapReduceFunction.register(
            map_func, reduce_func, axis=0, preserve_index=False
        )(self, **kwargs)