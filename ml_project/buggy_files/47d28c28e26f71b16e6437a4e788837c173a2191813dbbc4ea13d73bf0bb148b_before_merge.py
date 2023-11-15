    def show_hint(self, text, inspect_word, at_point):
        """Show code hint and crop text as needed."""
        # Check language
        lines = text.split('\n')
        is_signature = False
        if 'python' in self.language.lower():
            is_signature = '(' in lines[0]

        # Split signature and the rest
        signature, additional_text = None, text
        if is_signature:
            for i, line in enumerate(lines):
                if line.strip() == '':
                    break
            if i == 0:
                signature = lines[0]
                additional_text = None
            else:
                signature = '\n'.join(lines[:i])
                additional_text = '\n'.join(lines[i:])

            if signature:
                signature = self._format_signature(signature)

        # Check if signature and format
        point = self.get_word_start_pos(at_point)

        # This is needed to get hover hints
        cursor = self.cursorForPosition(at_point)
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        self._last_hover_cursor = cursor

        self.show_tooltip(signature=signature, text=additional_text,
                          at_point=point, inspect_word=inspect_word,
                          display_link=True, max_lines=10)