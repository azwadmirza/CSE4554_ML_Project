    def go_to_definition_from_cursor(self, cursor=None):
        """Go to definition from cursor instance (QTextCursor)"""
        if (not self.go_to_definition_enabled or
                not self.lsp_go_to_definition_enabled):
            return
        if cursor is None:
            cursor = self.textCursor()
        if self.in_comment_or_string():
            return
        # position = cursor.position()
        text = to_text_string(cursor.selectedText())
        if len(text) == 0:
            cursor.select(QTextCursor.WordUnderCursor)
            text = to_text_string(cursor.selectedText())
        if text is not None:
            # self.go_to_definition.emit(position)
            line, column = self.get_cursor_line_column()
            params = {
                'file': self.filename,
                'line': line,
                'column': column
            }
            return params