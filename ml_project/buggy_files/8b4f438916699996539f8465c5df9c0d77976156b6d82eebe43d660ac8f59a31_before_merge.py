    def get_current_word_and_position(self, completion=False):
        """Return current word, i.e. word at cursor position,
            and the start position"""
        cursor = self.textCursor()
        cursor_pos = cursor.position()

        if cursor.hasSelection():
            # Removes the selection and moves the cursor to the left side
            # of the selection: this is required to be able to properly
            # select the whole word under cursor (otherwise, the same word is
            # not selected when the cursor is at the right side of it):
            cursor.setPosition(min([cursor.selectionStart(),
                                    cursor.selectionEnd()]))
        else:
            # Checks if the first character to the right is a white space
            # and if not, moves the cursor one word to the left (otherwise,
            # if the character to the left do not match the "word regexp"
            # (see below), the word to the left of the cursor won't be
            # selected), but only if the first character to the left is not a
            # white space too.
            def is_space(move):
                curs = self.textCursor()
                curs.movePosition(move, QTextCursor.KeepAnchor)
                return not to_text_string(curs.selectedText()).strip()
            if not completion:
                if is_space(QTextCursor.NextCharacter):
                    if is_space(QTextCursor.PreviousCharacter):
                        return
                    cursor.movePosition(QTextCursor.WordLeft)
            else:
                def is_special_character(move):
                    curs = self.textCursor()
                    curs.movePosition(move, QTextCursor.KeepAnchor)
                    text_cursor = to_text_string(curs.selectedText()).strip()
                    return len(re.findall(r'([^\d\W]\w*)',
                                          text_cursor, re.UNICODE)) == 0
                if is_space(QTextCursor.PreviousCharacter):
                    return
                if (is_special_character(QTextCursor.NextCharacter)):
                    cursor.movePosition(QTextCursor.WordLeft)

        cursor.select(QTextCursor.WordUnderCursor)
        text = to_text_string(cursor.selectedText())
        # find a valid python variable name
        match = re.findall(r'([^\d\W]\w*)', text, re.UNICODE)
        if match:
            text, startpos = match[0], cursor.selectionStart()
            if completion:
                text = text[:cursor_pos - startpos]
            return text, startpos