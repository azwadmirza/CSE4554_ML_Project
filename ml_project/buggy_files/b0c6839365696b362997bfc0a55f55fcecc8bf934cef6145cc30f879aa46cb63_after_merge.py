    def _compute_lookup(self, row_loc, col_loc) -> Tuple[pandas.Index, pandas.Index]:
        if is_list_like(row_loc) and len(row_loc) == 1:
            if (
                isinstance(self.qc.index.values[0], np.datetime64)
                and type(row_loc[0]) != np.datetime64
            ):
                row_loc = [pandas.to_datetime(row_loc[0])]

        if isinstance(row_loc, slice):
            row_lookup = self.qc.index.to_series().loc[row_loc].values
        elif isinstance(self.qc.index, pandas.MultiIndex):
            row_lookup = self.qc.index[self.qc.index.get_locs(row_loc)]
        else:
            row_lookup = self.qc.index[self.qc.index.get_indexer_for(row_loc)]
        if isinstance(col_loc, slice):
            col_lookup = self.qc.columns.to_series().loc[col_loc].values
        elif isinstance(self.qc.columns, pandas.MultiIndex):
            col_lookup = self.qc.columns[self.qc.columns.get_locs(col_loc)]
        else:
            col_lookup = self.qc.columns[self.qc.columns.get_indexer_for(col_loc)]
        return row_lookup, col_lookup