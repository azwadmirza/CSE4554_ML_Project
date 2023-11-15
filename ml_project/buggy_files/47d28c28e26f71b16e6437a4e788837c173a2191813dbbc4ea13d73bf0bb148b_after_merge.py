    def show_hint(self, text, inspect_word, at_point):
        """Show code hint and crop text as needed."""
        # Check if signature and format
        res = self._check_signature_and_format(text)
        html_signature, extra_text, _ = res
        point = self.get_word_start_pos(at_point)

        # This is needed to get hover hints
        cursor = self.cursorForPosition(at_point)
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        self._last_hover_cursor = cursor

        self.show_tooltip(signature=html_signature, text=extra_text,
                          at_point=point, inspect_word=inspect_word,
                          display_link=True, max_lines=10)