    def run_selection(self):
        """
        Run selected text or current line in console.

        If some text is selected, then execute that text in console.

        If no text is selected, then execute current line, unless current line
        is empty. Then, advance cursor to next line. If cursor is on last line
        and that line is not empty, then add a new blank line and move the
        cursor there. If cursor is on last line and that line is empty, then do
        not move cursor.
        """
        text = self.get_current_editor().get_selection_as_executable_code()
        if text:
            self.exec_in_extconsole.emit(text, self.focus_to_editor)
            return
        editor = self.get_current_editor()
        line = editor.get_current_line()
        text = line.lstrip()
        if text:
            self.exec_in_extconsole.emit(text, self.focus_to_editor)
        if editor.is_cursor_on_last_line() and text:
            editor.append(editor.get_line_separator())
        editor.move_cursor_to_next('line', 'down')