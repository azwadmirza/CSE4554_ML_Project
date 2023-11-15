    def row_side_colors(self):
        var = self.annotation_color_var
        if var is None:
            return None
        column_data = column_data_from_table(self.input_data, var)
        span = (np.nanmin(column_data), np.nanmax(column_data))
        merges = self._merge_row_indices()
        if merges is not None:
            column_data = aggregate(var, column_data, merges)
        data, colormap = self._colorize(var, column_data)
        if var.is_continuous:
            colormap.span = span
        return data, colormap, var