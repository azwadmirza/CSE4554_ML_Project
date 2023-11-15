    def replace(self, to_replace=None, value=None, subset=None, inplace=False,
                limit=None, regex=False, method='pad'):
        """
        Returns a new DataFrame replacing a value with another value.

        Parameters
        ----------
        to_replace : int, float, string, or list
            Value to be replaced. If the value is a dict, then value is ignored and
            to_replace must be a mapping from column name (string) to replacement value.
            The value to be replaced must be an int, float, or string.
        value : int, float, string, or list
            Value to use to replace holes. The replacement value must be an int, float,
            or string. If value is a list, value should be of the same length with to_replace.
        subset : string, list
            Optional list of column names to consider. Columns specified in subset that
            do not have matching data type are ignored. For example, if value is a string,
            and subset contains a non-string column, then the non-string column is simply ignored.
        inplace : boolean, default False
            Fill in place (do not create a new object)

        Returns
        -------
        DataFrame
            Object after replacement.

        Examples
        --------
        >>> df = ks.DataFrame({"name": ['Ironman', 'Captain America', 'Thor', 'Hulk'],
        ...                    "weapon": ['Mark-45', 'Shield', 'Mjolnir', 'Smash']},
        ...                   columns=['name', 'weapon'])
        >>> df
                      name   weapon
        0          Ironman  Mark-45
        1  Captain America   Shield
        2             Thor  Mjolnir
        3             Hulk    Smash

        Scalar `to_replace` and `value`

        >>> df.replace('Ironman', 'War-Machine')
                      name   weapon
        0      War-Machine  Mark-45
        1  Captain America   Shield
        2             Thor  Mjolnir
        3             Hulk    Smash

        List like `to_replace` and `value`

        >>> df.replace(['Ironman', 'Captain America'], ['Rescue', 'Hawkeye'], inplace=True)
        >>> df
              name   weapon
        0   Rescue  Mark-45
        1  Hawkeye   Shield
        2     Thor  Mjolnir
        3     Hulk    Smash

        Replacing value by specifying column

        >>> df.replace('Mjolnir', 'Stormbuster', subset='weapon')
              name       weapon
        0   Rescue      Mark-45
        1  Hawkeye       Shield
        2     Thor  Stormbuster
        3     Hulk        Smash

        Dict like `to_replace`

        >>> df = ks.DataFrame({'A': [0, 1, 2, 3, 4],
        ...                    'B': [5, 6, 7, 8, 9],
        ...                    'C': ['a', 'b', 'c', 'd', 'e']},
        ...                   columns=['A', 'B', 'C'])

        >>> df.replace({'A': {0: 100, 4: 400}})
             A  B  C
        0  100  5  a
        1    1  6  b
        2    2  7  c
        3    3  8  d
        4  400  9  e

        >>> df.replace({'A': 0, 'B': 5}, 100)
             A    B  C
        0  100  100  a
        1    1    6  b
        2    2    7  c
        3    3    8  d
        4    4    9  e

        Notes
        -----
        One difference between this implementation and pandas is that it is necessary
        to specify the column name when you are passing dictionary in `to_replace`
        parameter. Calling `replace` on its index such as `df.replace({0: 10, 1: 100})` will
        throw an error. Instead specify column-name like `df.replace({'A': {0: 10, 1: 100}})`.
        """
        if method != 'pad':
            raise NotImplementedError("replace currently works only for method='pad")
        if limit is not None:
            raise NotImplementedError("replace currently works only when limit=None")
        if regex is not False:
            raise NotImplementedError("replace currently doesn't supports regex")

        if value is not None and not isinstance(value, (int, float, str, list, dict)):
            raise TypeError("Unsupported type {}".format(type(value)))
        if to_replace is not None and not isinstance(to_replace, (int, float, str, list, dict)):
            raise TypeError("Unsupported type {}".format(type(to_replace)))

        if isinstance(value, list) and isinstance(to_replace, list):
            if len(value) != len(to_replace):
                raise ValueError('Length of to_replace and value must be same')

        sdf = self._sdf.select(self._internal.data_columns)
        if isinstance(to_replace, dict) and value is None and \
                (not any(isinstance(i, dict) for i in to_replace.values())):
            sdf = sdf.replace(to_replace, value, subset)
        elif isinstance(to_replace, dict):
            for df_column, replacement in to_replace.items():
                if isinstance(replacement, dict):
                    sdf = sdf.replace(replacement, subset=df_column)
                else:
                    sdf = sdf.withColumn(df_column,
                                         F.when(scol_for(sdf, df_column) == replacement, value)
                                         .otherwise(scol_for(sdf, df_column)))

        else:
            sdf = sdf.replace(to_replace, value, subset)

        kdf = DataFrame(sdf)
        if inplace:
            self._internal = kdf._internal
        else:
            return kdf