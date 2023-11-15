    def get_word_at(self, coordinates):
        """Return word at *coordinates* (QPoint)."""
        cursor = self.cursorForPosition(coordinates)
        cursor.select(QTextCursor.WordUnderCursor)
        if self._is_point_inside_word_rect(coordinates):
            word = to_text_string(cursor.selectedText())
        else:
            word = ''

        return word