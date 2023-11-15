    def _reduce_for_stat_function(self, sfun, numeric_only=None):
        """
        :param sfun: the stats function to be used for aggregation
        :param numeric_only: not used by this implementation, but passed down by stats functions
        """
        from inspect import signature
        num_args = len(signature(sfun).parameters)
        col_sdf = self._scol
        col_type = self.schema[self.name].dataType
        if isinstance(col_type, BooleanType) and sfun.__name__ not in ('min', 'max'):
            # Stat functions cannot be used with boolean values by default
            # Thus, cast to integer (true to 1 and false to 0)
            # Exclude the min and max methods though since those work with booleans
            col_sdf = col_sdf.cast('integer')
        if num_args == 1:
            # Only pass in the column if sfun accepts only one arg
            col_sdf = sfun(col_sdf)
        else:  # must be 2
            assert num_args == 2
            # Pass in both the column and its data type if sfun accepts two args
            col_sdf = sfun(col_sdf, col_type)
        return _unpack_scalar(self._kdf._sdf.select(col_sdf))