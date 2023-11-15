    def clip(self, lower: Union[float, int] = None, upper: Union[float, int] = None) \
            -> 'DataFrame':
        """
        Trim values at input threshold(s).

        Assigns values outside boundary to boundary values.

        Parameters
        ----------
        lower : float or int, default None
            Minimum threshold value. All values below this threshold will be set to it.
        upper : float or int, default None
            Maximum threshold value. All values above this threshold will be set to it.

        Returns
        -------
        DataFrame
            DataFrame with the values outside the clip boundaries replaced.

        Examples
        --------
        >>> ks.DataFrame({'A': [0, 2, 4]}).clip(1, 3)
           A
        0  1
        1  2
        2  3

        Notes
        -----
        One difference between this implementation and pandas is that running
        pd.DataFrame({'A': ['a', 'b']}).clip(0, 1) will crash with "TypeError: '<=' not supported
        between instances of 'str' and 'int'" while ks.DataFrame({'A': ['a', 'b']}).clip(0, 1)
        will output the original DataFrame, simply ignoring the incompatible types.
        """
        if is_list_like(lower) or is_list_like(upper):
            raise ValueError("List-like value are not supported for 'lower' and 'upper' at the " +
                             "moment")

        if lower is None and upper is None:
            return self

        numeric_types = (DecimalType, DoubleType, FloatType, ByteType, IntegerType, LongType,
                         ShortType)
        numeric_columns = [(c, self._internal.scol_for(c)) for c in self.columns
                           if isinstance(self._internal.spark_type_for(c), numeric_types)]

        if lower is not None:
            numeric_columns = [(c, F.when(scol < lower, lower).otherwise(scol).alias(c))
                               for c, scol in numeric_columns]
        if upper is not None:
            numeric_columns = [(c, F.when(scol > upper, upper).otherwise(scol).alias(c))
                               for c, scol in numeric_columns]

        nonnumeric_columns = [self._internal.scol_for(c) for c in self.columns
                              if not isinstance(self._internal.spark_type_for(c), numeric_types)]

        sdf = self._sdf.select([scol for _, scol in numeric_columns] + nonnumeric_columns)

        return ks.DataFrame(sdf)[list(self.columns)]