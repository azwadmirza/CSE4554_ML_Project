    def _prepare_method(self, pandas_func, **kwargs):
        """Prepares methods given various metadata.
        Args:
            pandas_func: The function to prepare.

        Returns
            Helper function which handles potential transpose.
        """
        if self._is_transposed:

            def helper(df, internal_indices=[]):
                if len(internal_indices) > 0:
                    return pandas_func(
                        df.T, internal_indices=internal_indices, **kwargs
                    )
                return pandas_func(df.T, **kwargs)

        else:

            def helper(df, internal_indices=[]):
                if len(internal_indices) > 0:
                    return pandas_func(df, internal_indices=internal_indices, **kwargs)
                return pandas_func(df, **kwargs)

        return helper