    def load_more_data(self, value, rows=False, columns=False):
        old_selection = self.selectionModel().selection()
        old_rows_loaded = old_cols_loaded = None
        
        if rows and value == self.verticalScrollBar().maximum():
            old_rows_loaded = self.model().rows_loaded
            self.model().fetch_more(rows=rows)
            
        if columns and value == self.horizontalScrollBar().maximum():
            old_cols_loaded = self.model().cols_loaded
            self.model().fetch_more(columns=columns)
            
        if old_rows_loaded is not None or old_cols_loaded is not None:
            # if we've changed anything, update selection
            new_selection = QItemSelection()
            for part in old_selection:
                top = part.top()
                bottom = part.bottom()
                if (old_rows_loaded is not None and 
                    top == 0 and bottom == (old_rows_loaded-1)):
                    # complete column selected (so expand it to match updated range)
                    bottom = self.model().rows_loaded-1
                left = part.left()
                right = part.right()
                if (old_cols_loaded is not None
                    and left == 0 and right == (old_cols_loaded-1)):
                    # compete row selected (so expand it to match updated range)
                    right = self.model().cols_loaded-1
                top_left = self.model().index(top, left)
                bottom_right = self.model().index(bottom, right)
                part = QItemSelectionRange(top_left, bottom_right)
                new_selection.append(part)
            self.selectionModel().select(new_selection, self.selectionModel().ClearAndSelect)