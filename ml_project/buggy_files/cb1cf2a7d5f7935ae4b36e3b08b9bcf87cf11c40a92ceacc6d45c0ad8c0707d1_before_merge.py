    def _default_to_pandas(self, f, **kwargs):
        """Defailts the execution of this function to pandas.

        Args:
            f: The function to apply to each group.

        Returns:
             A new Modin DataFrame with the result of the pandas function.
        """
        if isinstance(self._by, type(self._query_compiler)):
            by = self._by.to_pandas().squeeze()
        else:
            by = self._by

        def groupby_on_multiple_columns(df):
            return f(df.groupby(by=by, axis=self._axis, **self._kwargs), **kwargs)

        return self._df._default_to_pandas(groupby_on_multiple_columns)