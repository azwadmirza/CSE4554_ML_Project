    def isin(self, values):
        """
        Whether each element in the DataFrame is contained in values.

        Parameters
        ----------
        values : iterable or dict
           The sequence of values to test. If values is a dict,
           the keys must be the column names, which must match.
           Series and DataFrame are not supported.

        Returns
        -------
        DataFrame
            DataFrame of booleans showing whether each element in the DataFrame
            is contained in values.

        Examples
        --------
        >>> df = ks.DataFrame({'num_legs': [2, 4], 'num_wings': [2, 0]},
        ...                   index=['falcon', 'dog'],
        ...                   columns=['num_legs', 'num_wings'])
        >>> df
                num_legs  num_wings
        falcon         2          2
        dog            4          0

        When ``values`` is a list check whether every value in the DataFrame
        is present in the list (which animals have 0 or 2 legs or wings)

        >>> df.isin([0, 2])
                num_legs  num_wings
        falcon      True       True
        dog        False       True

        When ``values`` is a dict, we can pass values to check for each
        column separately:

        >>> df.isin({'num_wings': [0, 3]})
                num_legs  num_wings
        falcon     False      False
        dog        False       True
        """
        if isinstance(values, (pd.DataFrame, pd.Series)):
            raise NotImplementedError("DataFrame and Series are not supported")
        if isinstance(values, dict) and not set(values.keys()).issubset(self.columns):
            raise AttributeError(
                "'DataFrame' object has no attribute %s"
                % (set(values.keys()).difference(self.columns)))

        _select_columns = self._internal.index_columns.copy()
        if isinstance(values, dict):
            for col in self.columns:
                if col in values:
                    _select_columns.append(self._internal.scol_for(col)
                                           .isin(values[col]).alias(col))
                else:
                    _select_columns.append(F.lit(False).alias(col))
        elif is_list_like(values):
            _select_columns += [
                self._internal.scol_for(col).isin(list(values)).alias(col)
                for col in self.columns]
        else:
            raise TypeError('Values should be iterable, Series, DataFrame or dict.')

        return DataFrame(self._internal.copy(sdf=self._sdf.select(_select_columns)))