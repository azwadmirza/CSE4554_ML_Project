    def go_to_definition_from_cursor(self, cursor=None):
        """Go to definition from cursor instance (QTextCursor)"""
        if (not self.go_to_definition_enabled or
                self.in_comment_or_string()):
            return
        if cursor is None:
            cursor = self.textCursor()
        text = to_text_string(cursor.selectedText())
        if len(text) == 0:
            cursor.select(QTextCursor.WordUnderCursor)
            text = to_text_string(cursor.selectedText())
        if text is not None:
            line, column = self.get_cursor_line_column()
            params = {
                'file': self.filename,
                'line': line,
                'column': column
            }
            return params