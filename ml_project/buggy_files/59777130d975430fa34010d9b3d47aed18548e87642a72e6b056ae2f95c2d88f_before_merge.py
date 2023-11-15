    def __exec_cell(self):
        ls = self.get_line_separator()
        init_cursor = QTextCursor(self.textCursor())
        start_pos, end_pos = self.__save_selection()
        cursor, whole_file_selected = self.select_current_cell()
        self.setTextCursor(cursor)
        line_from, line_to = self.get_selection_bounds()
        text = self.get_selection_as_executable_code()
        self.last_cursor_cell = init_cursor
        self.__restore_selection(start_pos, end_pos)
        if text is not None:
            text = text.rstrip()
            text = ls * line_from + text
        return text, line_from