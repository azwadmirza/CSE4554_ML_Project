    def _process_text(self, text):
        if self.is_snippet_active:
            line, column = self.editor.get_cursor_line_column()
            # Update placeholder text node
            if text != '\b':
                self.insert_text(text, line, column)
            elif text == '\n':
                self.reset()
            else:
                self.delete_text(line, column)
            self._update_ast()
            self.redo_stack = []