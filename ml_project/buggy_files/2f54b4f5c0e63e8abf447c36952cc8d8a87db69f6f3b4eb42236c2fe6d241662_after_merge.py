    def load_more_data(self, value, rows=False, columns=False):
        """Load more rows and columns to display."""
        try:
            if rows and value == self.verticalScrollBar().maximum():
                self.model().fetch_more(rows=rows)
                self.sig_fetch_more_rows.emit()
            if columns and value == self.horizontalScrollBar().maximum():
                self.model().fetch_more(columns=columns)
                self.sig_fetch_more_columns.emit()

        except NameError:
            # Needed to handle a NameError while fetching data when closing
            # See issue 7880
            pass