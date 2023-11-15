    def _reduce_for_stat_function(self, sfun, numeric_only=False):
        """
        Applies sfun to each column and returns a pd.Series where the number of rows equal the
        number of columns.

        Parameters
        ----------
        sfun : either an 1-arg function that takes a Column and returns a Column, or
        a 2-arg function that takes a Column and its DataType and returns a Column.
        numeric_only : boolean, default False
            If True, sfun is applied on numeric columns (including booleans) only.
        """
        from inspect import signature
        exprs = []
        num_args = len(signature(sfun).parameters)
        for col in self.columns:
            col_sdf = self._sdf[col]
            col_type = self._sdf.schema[col].dataType

            is_numeric_or_boolean = isinstance(col_type, (NumericType, BooleanType))
            min_or_max = sfun.__name__ in ('min', 'max')
            keep_column = not numeric_only or is_numeric_or_boolean or min_or_max

            if keep_column:
                if isinstance(col_type, BooleanType) and not min_or_max:
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
                exprs.append(col_sdf.alias(col))

        sdf = self._sdf.select(*exprs)
        pdf = sdf.toPandas()
        assert len(pdf) == 1, (sdf, pdf)
        row = pdf.iloc[0]
        row.name = None
        return row  # Return first row as a Series