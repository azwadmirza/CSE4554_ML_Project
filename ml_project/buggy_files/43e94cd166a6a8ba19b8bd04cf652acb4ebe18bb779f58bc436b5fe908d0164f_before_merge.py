    def _sel_to_text(self, cell_range):
        """Copy an array portion to a unicode string"""
        if not cell_range:
            return
        row_min, row_max, col_min, col_max = get_idx_rect(cell_range)
        if col_min == 0 and col_max == (self.model().cols_loaded-1):
            # we've selected a whole column. It isn't possible to
            # select only the first part of a column without loading more, 
            # so we can treat it as intentional and copy the whole thing
            col_max = self.model().total_cols-1
        if row_min == 0 and row_max == (self.model().rows_loaded-1):
            row_max = self.model().total_rows-1
        
        _data = self.model().get_data()
        if PY3:
            output = io.BytesIO()
        else:
            output = io.StringIO()
        try:
            np.savetxt(output, _data[row_min:row_max+1, col_min:col_max+1],
                       delimiter='\t')
        except:
            QMessageBox.warning(self, _("Warning"),
                                _("It was not possible to copy values for "
                                  "this array"))
            return
        contents = output.getvalue().decode('utf-8')
        output.close()
        return contents