    def _reindex_columns(self, columns):
        label_columns = list(columns)
        null_columns = [
            F.lit(np.nan).alias(label_column) for label_column
            in label_columns if label_column not in self.columns]

        # Concatenate all fields
        sdf = self._sdf.select(
            self._internal.index_scols +
            list(map(self._internal.scol_for, self.columns)) +
            null_columns)

        # Only select label_columns (with index columns)
        sdf = sdf.select(self._internal.index_scols + [scol_for(sdf, col) for col in label_columns])
        return self._internal.copy(
            sdf=sdf,
            data_columns=label_columns)