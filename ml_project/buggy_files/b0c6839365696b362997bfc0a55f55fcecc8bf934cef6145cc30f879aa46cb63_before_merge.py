    def _compute_lookup(self, row_loc, col_loc) -> Tuple[pandas.Index, pandas.Index]:
        if isinstance(row_loc, list) and len(row_loc) == 1:
            if (
                isinstance(self.qc.index.values[0], np.datetime64)
                and type(row_loc[0]) != np.datetime64
            ):
                row_loc = [pandas.to_datetime(row_loc[0])]
        row_lookup = self.qc.index.to_series().loc[row_loc].index
        col_lookup = self.qc.columns.to_series().loc[col_loc].index
        return row_lookup, col_lookup