    def __exec_cell(self, cursor=None):
        """Get text and line number from cursor or current position."""
        if cursor is None:
            cursor = self.textCursor()
        ls = self.get_line_separator()
        cursor, whole_file_selected = self.select_current_cell(cursor)
        line_from, line_to = self.get_selection_bounds(cursor)
        block = self.get_selection_first_block(cursor)
        text = self.get_selection_as_executable_code(cursor)

        if text is not None:
            text = ls * line_from + text
        return text, block