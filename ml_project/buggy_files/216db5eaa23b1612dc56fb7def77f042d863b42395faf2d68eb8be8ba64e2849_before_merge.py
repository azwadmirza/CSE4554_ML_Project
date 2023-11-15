    def __getitem__(self, key):
        if self._ks is None and (not isinstance(key, tuple) or len(key) != 2):
            raise TypeError("Use DataFrame.at like .at[row_index, column_name]")
        if self._ks is not None and not isinstance(key, str) and len(key) != 1:
            raise TypeError("Use Series.at like .at[row_index]")

        # TODO Maybe extend to multilevel indices in the future
        if len(self._kdf._internal.index_columns) != 1:
            raise ValueError("'.at' only supports indices with level 1 right now")

        column = key[1] if self._ks is None else self._ks.name
        if column is not None and column not in self._kdf._internal.data_columns:
            raise KeyError("%s" % column)
        series = self._ks if self._ks is not None else self._kdf[column]

        row = key[0] if self._ks is None else key
        pdf = (series._kdf._sdf
               .where(F.col(self._kdf._internal.index_columns[0]) == row)
               .select(column)
               .toPandas())
        if len(pdf) < 1:
            raise KeyError("%s" % row)

        values = pdf.iloc[:, 0].values
        return values[0] if len(values) == 1 else values