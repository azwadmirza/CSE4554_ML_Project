    def describe(self, percentiles=None, include=None, exclude=None):
        """
        Generates descriptive statistics that summarize the central tendency,
        dispersion and shape of a dataset's distribution, excluding NaN values.

        Args:
            percentiles (list-like of numbers, optional):
                The percentiles to include in the output.
            include: White-list of data types to include in results
            exclude: Black-list of data types to exclude in results

        Returns: Series/DataFrame of summary statistics
        """
        if include is not None:
            if not is_list_like(include):
                include = [include]
            include = [np.dtype(i) for i in include]
        if exclude is not None:
            if not is_list_like(include):
                exclude = [exclude]
            exclude = [np.dtype(e) for e in exclude]
        if percentiles is not None:
            pandas.DataFrame()._check_percentile(percentiles)
        return DataFrame(
            query_compiler=self._query_compiler.describe(
                percentiles=percentiles, include=include, exclude=exclude
            )
        )