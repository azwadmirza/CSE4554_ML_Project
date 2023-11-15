    def find_text(self, text, changed=True, forward=True, case=False,
                  words=False, regexp=False):
        """Find text"""
        cursor = self.textCursor()
        findflag = QTextDocument.FindFlag()

        if not forward:
            findflag = findflag | QTextDocument.FindBackward

        if case:
            findflag = findflag | QTextDocument.FindCaseSensitively

        moves = [QTextCursor.NoMove]
        if forward:
            moves += [QTextCursor.NextWord, QTextCursor.Start]
            if changed:
                if to_text_string(cursor.selectedText()):
                    new_position = min([cursor.selectionStart(),
                                        cursor.selectionEnd()])
                    cursor.setPosition(new_position)
                else:
                    cursor.movePosition(QTextCursor.PreviousWord)
        else:
            moves += [QTextCursor.End]

        if regexp:
            text = to_text_string(text)
        else:
            text = re.escape(to_text_string(text))

        if QT55_VERSION:
            pattern = QRegularExpression(u"\\b{}\\b".format(text) if words else
                                         text)
            if case:
                pattern.setPatternOptions(
                    QRegularExpression.CaseInsensitiveOption)
        else:
            pattern = QRegExp(u"\\b{}\\b".format(text)
                              if words else text, Qt.CaseSensitive if case else
                              Qt.CaseInsensitive, QRegExp.RegExp2)

        for move in moves:
            cursor.movePosition(move)
            if regexp and '\\n' in text:
                # Multiline regular expression
                found_cursor = self.find_multiline_pattern(pattern, cursor,
                                                           findflag)
            else:
                # Single line find: using the QTextDocument's find function,
                # probably much more efficient than ours
                found_cursor = self.document().find(pattern, cursor, findflag)
            if found_cursor is not None and not found_cursor.isNull():
                self.setTextCursor(found_cursor)
                return True

        return False