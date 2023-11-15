    def _reindex_columns(self, columns):
        label_columns = list(columns)
        null_columns = [
            F.lit(np.nan).alias(label_column) for label_column
            in label_columns if label_column not in self.columns]

        # Concatenate all fields
        sdf = self._sdf.select(
            self._internal.index_columns +
            list(map(F.col, self.columns)) +
            null_columns)

        # Only select label_columns (with index columns)
        sdf = sdf.select(self._internal.index_columns + label_columns)
        return self._internal.copy(
            sdf=sdf,
            data_columns=label_columns)